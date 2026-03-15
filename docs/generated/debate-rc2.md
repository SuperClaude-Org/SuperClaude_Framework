# Adversarial Debate: RC-2 is the True Root Cause

**Position**: The multi-file accumulation design defect (RC-2) is the primary root cause of the `OSError: [Errno 7] Argument list too long` crash at the `spec-fidelity` step.

**Assigned side**: RC-2

---

## Position Statement

The crash did not happen because a constant was miscalibrated. The crash did not happen because the wrong transport mechanism was chosen. The crash happened because `_embed_inputs()` was designed to handle a single file and was silently reused for multi-file steps without any modification to its size-checking logic. The spec-fidelity step passes two inputs totalling 152.1 KB of raw content — neither of which breaches 128 KB individually. The design never modelled the case where accumulation of individually-safe inputs creates a combined payload that is unsafe. That modelling failure is the root cause.

RC-1 and RC-3 are real issues. RC-1 describes a guard that was set too high. RC-3 describes a transport mechanism with a hard ceiling. But neither of them is the *primary* root cause in the sense that matters: the cause whose correction would have prevented this specific crash. If you fix RC-1 by setting `_EMBED_SIZE_LIMIT` to 128 KB, you do not fix this crash — because 155.7 KB still exceeds 128 KB. If you fix RC-3 by switching to a file-based transport, you fix the crash but you have over-engineered past the actual problem. RC-2 is the defect that made two safe inputs combine into an unsafe payload without detection. RC-2 is where the logic should have caught this.

---

## Argument for RC-2

### The Causal Chain

The crash trace is:

1. `spec-fidelity` step is constructed with `inputs=[config.spec_file, merge_file]` — two files, 117.9 KB and 34.2 KB.
2. `roadmap_run_step()` calls `_embed_inputs(step.inputs)`.
3. `_embed_inputs()` reads both files, wraps each in a fenced block with a `# <path>` header, joins them with `\n\n`. The result is a single concatenated string of roughly 155.7 KB.
4. The size check `len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT` evaluates `155.7 KB <= 200 KB` → `True`. The fallback never fires.
5. `effective_prompt = step.prompt + "\n\n" + embedded` appends 155.7 KB to the base prompt.
6. `build_command()` places this full string as the `-p <prompt>` argument.
7. `subprocess.Popen()` attempts to exec the process. The kernel rejects it: the `-p` argument alone exceeds `MAX_ARG_STRLEN` (128 KB).
8. `OSError: [Errno 7] Argument list too long`.

At step 3, the design makes a silent assumption: that the concatenated result of all inputs will be safe if it stays under the guard threshold. That assumption is structurally wrong for any multi-file step, because the guard threshold has no relationship to per-file sizes and no awareness that accumulation can combine safe components into an unsafe whole.

### The Design Assumption That Is Not There

Read `_embed_inputs()` carefully:

```python
def _embed_inputs(input_paths: list[Path]) -> str:
    if not input_paths:
        return ""
    blocks: list[str] = []
    for p in input_paths:
        content = Path(p).read_text(encoding="utf-8")
        blocks.append(f"# {p}\n```\n{content}\n```")
    return "\n\n".join(blocks)
```

There is no per-file size check. There is no early-exit if a single file is already large. There is no cap on how many files can be embedded. The function returns the full concatenation unconditionally. It was written assuming that any size checking would happen at the call site — which it does, but only on the total, and only against a guard constant that was already wrong.

The call site:

```python
embedded = _embed_inputs(step.inputs)
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded
    extra_args: list[str] = []
elif embedded:
    # fallback
```

The fallback exists. It was written by someone who understood that large inputs could cause problems. But the threshold that decides when to use it was calibrated for a world where the embedded content comes from a single file. When a second file was added to the spec-fidelity step's `inputs` list, no one updated the threshold reasoning to account for the fact that two files now accumulate.

### What "Fix RC-2" Means and Why It Would Have Prevented the Crash

A correct multi-file accumulation model would have done one of the following:

**Option A — Per-file threshold**: Check each individual file against a per-file limit before deciding to embed it. If any single file exceeds, say, 64 KB (leaving headroom for the other file and the base prompt), fall back to `--file` for all inputs.

**Option B — Budget-aware accumulation**: Track remaining budget as files are added. Stop embedding when the running total would exceed the safe threshold. Switch the remaining files to `--file`.

**Option C — Hard multi-file rule**: If `len(input_paths) > 1`, always use `--file` flags regardless of size, because multi-file accumulation is inherently unpredictable.

Any of these would have caught the spec-fidelity case. The 117.9 KB spec alone already consumed 92% of `MAX_ARG_STRLEN`. Adding any second file of meaningful size would exceed it. An accumulation-aware model would have seen this and routed to the fallback. The crash would not have happened.

### The Concrete Evidence That This Is a Design Defect, Not a Calibration Error

The RCA document notes: "The same crash occurred at the `extract` step against this spec before file condensing." This is critical. The extract step uses a single input — `config.spec_file`. When the spec was larger, the single-file embed exceeded 128 KB by itself and crashed. The spec was then condensed to 117.9 KB. Now the extract step passes — 117.9 KB is below 128 KB. But spec-fidelity adds a second file (34.2 KB), and the crash returns.

This history reveals two separate failure modes that share the same design gap:

- **Single large file**: 117.9 KB solo is 92% of the limit. Marginally safe, accidentally.
- **Two medium files**: 117.9 + 34.2 = 152.1 KB combined is 19% over the limit. Structurally unsafe.

RC-1 would have fixed the first failure mode if `_EMBED_SIZE_LIMIT` had been 128 KB — the single file would have triggered the fallback. But RC-1 does not fix the second failure mode: even with `_EMBED_SIZE_LIMIT = 128 KB`, a file at 117.9 KB passes the guard, gets embedded, and then the second file is added to the combined string, pushing it past 128 KB before the prompt is even appended.

Wait — re-read the code. The guard checks the total `embedded` string, not per file. So if `_EMBED_SIZE_LIMIT = 128 KB`, the 155.7 KB combined embed would fail the check (`155.7 > 128`), and the fallback would fire. That means RC-1 *would* fix this specific crash if the guard was corrected to 128 KB.

This is the steelman for RC-1, and I will address it properly in the Steelman section. The key rebuttal is: fixing RC-1 treats the symptom of this incident but not the class of defect. The design is still fragile because:

1. The guard is compared against the combined embed, which means adding a third small file to any future step could push a previously-safe pipeline back into the failure zone without any warning.
2. Two individually-safe files (say, 70 KB each = 140 KB combined) would exceed a 128 KB guard, triggering the fallback — but neither file is individually dangerous, and a smarter accumulation model would have caught this with per-file reasoning.
3. The guard constant will be wrong again. It was changed from 100 KB (the comment) to 200 KB (the value) at some unknown point. It will be changed again. If the design depended on a single constant being calibrated exactly right, the design is one number away from the same class of crash.

---

## Attack on RC-1

### RC-1's Claim

RC-1 argues that the root cause is the miscalibrated constant: `_EMBED_SIZE_LIMIT = 200 * 1024` instead of `128 * 1024`. The guard was designed to prevent OS-level failures. Its threshold is 56% above the actual OS limit. If it had been set correctly, the fallback would have fired and the crash would not have occurred.

This is true for this specific incident. It is not true as a general defense.

### Attack 1: Fixing the Constant Does Not Fix the Design

If `_EMBED_SIZE_LIMIT` is changed to 128 KB, the next pipeline step that takes three inputs of 50 KB each would produce a 150 KB embed, exceed the guard, and fall back to `--file`. Fine. But what about a step that takes four inputs of 35 KB each? 140 KB — exceeds 128 KB, fallback triggers. What about five inputs of 28 KB each? 140 KB — same result. In each case the fallback saves you.

But now change the question: what if a future step has one large input (say, 100 KB) and the system designer assumes that since the limit is 128 KB, there is 28 KB of headroom for the base prompt? If the prompt template grows slightly — perhaps a new instruction block is added — the *base prompt* plus the embedded input can push past 128 KB even with only one file. RC-1's fix re-calibrates the guard but does not address the architectural reality that the base prompt also contributes to the total argument size.

The code does not check `len((step.prompt + "\n\n" + embedded).encode("utf-8"))`. It checks `len(embedded.encode("utf-8"))`. The guard is not checking what actually gets passed to `-p`. It is checking only the embedded portion. This means even a perfectly calibrated guard can be wrong by the size of the base prompt.

### Attack 2: The Comment/Value Mismatch Proves the Constant Is Untrustworthy

The code reads: `_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB`. The comment says 100 KB. The value says 200 KB. This is not a minor inconsistency — it reveals that someone changed the constant without understanding what constraint it was enforcing. The original author wrote 100 KB and commented it. A later change doubled it without updating the comment, without running any analysis of what the OS constraint actually was.

This is not an argument that the constant being wrong is an incidental mistake that can be corrected once and trusted. This is evidence that the constant-based approach is fragile by design. Any constant that can be changed without visible consequences — no test failure, no immediate crash, just a wider window of silent danger — will eventually be changed incorrectly again. RC-1's "fix" is to correct the constant. The same class of problem will recur the next time someone touches it.

### Attack 3: RC-1 Is Downstream of RC-2

Even if you accept that the wrong constant caused this crash, you have to ask: *why* was the wrong constant dangerous? Because two files were being accumulated without per-file awareness. If the design had been per-file safe — refusing to embed any file over, say, 60 KB, or tracking remaining budget per file — the total would never have reached a point where the guard constant mattered. The constant being wrong only mattered because the accumulation was already producing a combined payload that was unsafe.

RC-1 is a condition that made the crash happen in this exact incident. RC-2 is the design gap that made the system incapable of handling multi-file accumulation safely regardless of where the constant was set.

---

## Attack on RC-3

### RC-3's Claim

RC-3 argues that the architectural problem is passing the prompt as a CLI argument (`-p <text>`), creating a hard ceiling that no calibration of `_EMBED_SIZE_LIMIT` can fully solve. The base prompt plus any embedded content must fit inside 128 KB. As specs and prompt templates grow, even zero embedded content may eventually exceed the limit.

### Attack 1: RC-3 Is a Future Risk, Not the Present Cause

The actual crash at spec-fidelity was caused by 155.7 KB of embedded content being passed as `-p`. The base prompt by itself (without embedded content) is not reported to be near the 128 KB limit. RC-3's claim — that the base prompt alone could eventually breach the limit — is speculative and not demonstrated by the evidence. There is no measurement in the RCA showing that the base prompt template is anywhere close to 128 KB.

A root cause that describes a future failure mode, not the present one, is an architectural concern, not the root cause of this incident.

### Attack 2: The `--file` Fallback Already Solves RC-3's Core Problem

RC-3 argues that the `-p` transport mechanism is the wrong choice for large payloads. But the codebase already has a fallback: when the embedded content is too large, it falls back to `--file` for the input files. The `--file` flags pass file paths, not file contents, through the argument list. This routes the large content through a mechanism (file I/O) that is not subject to `MAX_ARG_STRLEN`.

If the `--file` fallback fires correctly — which it does when `_EMBED_SIZE_LIMIT` is properly calibrated and the multi-file accumulation is handled correctly — the `-p` argument contains only the base prompt template, which is a small, bounded string. The architectural ceiling RC-3 describes is only reached if the embed logic fails to use the fallback. The fallback exists. The fallback works. The problem is that it is not triggered at the right time.

RC-3 says "no calibration of `_EMBED_SIZE_LIMIT` can fully solve it because the base prompt + template will eventually hit 128 KB." This is true in a theoretical long-term sense. But the base prompt template would have to grow to 128 KB of instructions before this matters. That is not an accidental edge case — it would require the template to expand by an order of magnitude. This is not a present architectural constraint; it is a future scalability concern.

### Attack 3: RC-3's Fix Over-Engineers the Problem

If RC-3 is accepted as the root cause, the fix is to change the transport mechanism — write the prompt to a temp file, pass a `--prompt-file` flag (if one exists), or use stdin. This is a significant engineering change. It modifies the interface between the orchestrator and the `claude` CLI in a way that affects every step, not just multi-file steps. It introduces new failure modes (temp file creation, cleanup, path handling, process stdin handling).

The actual problem is that two files of known sizes were accumulated without budget awareness. The fix for that is local, targeted, and testable: add per-file size reasoning to `_embed_inputs()` or its call site. Changing the transport mechanism to fix an accumulation bug is the wrong level of abstraction.

RC-3 correctly identifies a real architectural constraint. It incorrectly frames that constraint as the root cause of a bug that was caused by missing accumulation logic.

---

## Steelman + Refutation

### Steelman: RC-1

**Strongest version**: The guard was purpose-built to prevent OS argument list failures. Its specification is clear: if the embedded content would cause an OS failure, use `--file` instead. The guard is specified in a comment that said `# 100 KB` — close to the actual `MAX_ARG_STRLEN` of 128 KB — and was then incorrectly doubled to 200 KB. With `_EMBED_SIZE_LIMIT = 128 KB`, the 155.7 KB combined embed would have correctly failed the guard and triggered the fallback. The crash would not have occurred. The guard is the designed defense layer. It was breached because of a specific, identified, fixable miscalibration. Fix the constant, fix the crash. Everything else is a secondary concern.

**Refutation**: This argument is correct in the narrow incident scope. But it confuses "fix that would have prevented this crash" with "fix that correctly models the problem." There are three separate things the guard is failing to account for:

1. It checks only the embedded portion, not `step.prompt + embedded` (the full `-p` argument). A base prompt of 30 KB plus an embedded portion of 100 KB totals 130 KB and would pass a 128 KB guard on the embedded portion alone, yet still crash.

2. Two files of 70 KB each total 140 KB. A guard at 128 KB would correctly catch this. But the reason they combine past the limit is accumulation, not any individual file being oversized. The guard at 128 KB is a total guard, not a structural guard. It catches accumulation by accident, not by design.

3. The guard constant will be changed again. It has already been changed once incorrectly. The `# 100 KB` comment demonstrates that the intended value was 100 KB, not 200 KB. Someone changed it without understanding the OS constraint. A design that depends on a single magic constant staying correctly calibrated is fragile. The multi-file accumulation model is the design defect that makes any calibration of the constant feel like guessing.

Correcting the constant is a necessary repair. It is not a sufficient architectural fix. RC-1 is a contributing factor and a symptom of RC-2.

### Steelman: RC-3

**Strongest version**: Even if you fix the constant and add per-file size checks, you are still betting that the base prompt template will stay small. You are still passing potentially large strings through a kernel-constrained argument slot. The `--file` fallback is a partial solution — it moves the input file content out of the argument, but the base prompt stays in `-p`. As prompt templates grow (adding more instructions, context, examples), the base prompt alone could breach 128 KB. At that point, no amount of embed limiting helps. The only real fix is to change how the prompt is delivered: write it to a file, pipe it through stdin, or find a `--prompt-file` equivalent. Until that architectural change is made, the system is one large prompt template away from the same class of crash.

**Refutation**: This argument describes a real long-term risk. It does not describe the present root cause. The base prompt templates in this codebase are instruction text, not document content. They are bounded in a way that embedded file content is not. A prompt template that grows to 128 KB would require deliberate, extensive authoring — it would not happen accidentally. Embedded file content, by contrast, grows as the user's spec grows, which is organic and uncontrolled.

More importantly, RC-3's fix — changing the transport mechanism — solves RC-2 as a side effect (because file content no longer goes through `-p` at all). This means RC-3 is a superset fix, not a more accurate root cause diagnosis. The question is not "what fix addresses the most surface area" but "what design gap caused this specific crash." That gap is the accumulation model, not the transport mechanism. The transport mechanism has a fallback that handles exactly the problem RC-3 describes. The fallback was not triggered because the accumulation logic was wrong. Fix the accumulation logic, and the transport mechanism works as designed.

---

## Likelihood Scores

| Root Cause | Likelihood Score (0–100) | Reasoning |
|---|---|---|
| **RC-1: Miscalibrated `_EMBED_SIZE_LIMIT`** | 25 | Real and necessary to fix. Would have prevented this specific crash if corrected. But does not address the structural gap: multi-file accumulation is not modelled, and the constant is not checked against the full `-p` argument size. Correcting it is a repair, not a fix. |
| **RC-2: Multi-file accumulation not modelled** | 55 | The direct structural cause of the crash. Neither input file was individually unsafe. Their combination was. The design had no mechanism to reason about accumulation across files. Even if RC-1 were corrected, the design would remain fragile for any pipeline step where input count or per-file sizes change organically. This is the defect that should be fixed to prevent the class of crash, not just this instance. |
| **RC-3: CLI argument transport mechanism** | 20 | Identifies a real architectural ceiling. Correctly describes why the base prompt is also a risk. But the ceiling has not been reached — the crash was caused by embedded content, and the fallback mechanism exists to route embedded content out of the argument list. RC-3 is a future risk and a secondary concern, not the primary cause of this incident. |

**Note**: Scores do not sum to 100 because they reflect independent likelihood assessments of each RC being the *primary* cause, not mutually exclusive probabilities. All three are real; the debate is about primacy.

---

## Verdict

RC-2 is the primary root cause.

The causal chain is clear: two files, individually safe, were accumulated into a combined payload with no per-file or budget-aware logic. The design of `_embed_inputs()` and its call site assumes that the total-size check is sufficient. It is not. Total-size sufficiency assumes a single-file model or a model where the guard is set well below the OS limit with enough margin to absorb any second file. Neither assumption holds here.

RC-1 contributed to the crash in this incident because the miscalibrated constant allowed 155.7 KB to pass the guard. But RC-1 is downstream of RC-2: the constant only mattered because the accumulation had already produced an unsafe total. If the accumulation model had been correct — declining to embed combinations of files that together approached the OS limit — the constant's value would have been irrelevant for this case.

RC-3 identifies a real architectural constraint that the codebase should eventually address. It is not the root cause of this incident because the `-p` transport mechanism has a working fallback that correctly avoids the OS limit when triggered. The fallback was not triggered because RC-2 allowed the unsafe accumulation to pass the guard check.

The fix that addresses RC-2 also closes RC-1 as a meaningful risk: if per-file or budget-aware accumulation logic routes to `--file` before any single-file or combined content approaches the OS limit, the constant's calibration matters far less. A guard constant with a large margin is a last-resort catch. It should not be the first and only line of defense. RC-2 is the defect that made it the only line of defense, and that line was set in the wrong place.

**Fix priority**: Address RC-2 by adding accumulation-aware logic to `_embed_inputs()` or its call site. Correct RC-1 as a necessary accompanying repair. Document RC-3 as a future architectural risk with a clear trigger condition (base prompt template approaching 64 KB).
