# Adversarial Debate: RC-1 is the True Root Cause

**Position**: `_EMBED_SIZE_LIMIT` miscalibration at 200 KB is the primary root cause of the `OSError: [Errno 7] Argument list too long` crash in the `spec-fidelity` step.

---

## Position Statement

The crash is not an accident of input size, nor is it an inherent architectural flaw. It is the direct consequence of a guard that was written to prevent exactly this failure and was then set to a value that makes it inoperative for the scenario it was designed to handle. The guard had one job. It failed that job because someone changed `100 * 1024` to `200 * 1024` and did not update the comment or verify the OS constraint. Every other factor in this crash is a precondition that the guard was supposed to absorb. RC-1 is the correct diagnosis.

---

## Argument for RC-1

### The causal chain is direct and unambiguous

The code in `executor.py` at line 175 reads:

```python
_EMBED_SIZE_LIMIT = 200 * 1024  # 100 KB

if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded
    extra_args: list[str] = []
elif embedded:
    # fallback: use --file flags instead
    effective_prompt = step.prompt
    extra_args = [arg for input_path in step.inputs for arg in ("--file", str(input_path))]
```

This is not ambiguous. The guard's purpose, stated explicitly in the comment on line 53 — `# Threshold above which inline embedding falls back to --file flags` — is to prevent the embedded prompt from being passed as a CLI `-p` argument when the content is too large for the OS to handle. The fallback path (using `--file` flags) exists precisely because the developer who wrote this code understood that large payloads cannot be passed as CLI arguments.

The causal chain:
1. `_EMBED_SIZE_LIMIT` is set to 200 KB.
2. Linux `MAX_ARG_STRLEN` is 128 KB per argument.
3. The embedded prompt is 155.7 KB — above the OS limit, below the guard.
4. The guard evaluates `155.7 KB <= 200 KB` as `True`.
5. The embedded content is placed inline into `effective_prompt`.
6. `ClaudeProcess.build_command()` passes `effective_prompt` as the `-p` argument.
7. `subprocess.Popen` calls `execve`, which rejects the argument.
8. `OSError: [Errno 7] Argument list too long`.

Step 4 is where the system fails. If `_EMBED_SIZE_LIMIT` were set to any value at or below 128 KB — which is what the comment says it should be — the guard would have evaluated `155.7 KB <= 100 KB` as `False`, the fallback branch would have fired, and the crash would not have occurred. Full stop.

### The comment is a confession

The comment reads `# 100 KB` while the value is `200 * 1024`. This is not a documentation inconsistency — it is forensic evidence that the constant was originally 100 KB and was changed. Someone increased the threshold, either to accommodate growing inputs or to silence a warning that was triggering too aggressively, without understanding that the original value was calibrated against a hard OS constraint, not an arbitrary preference. The comment wasn't updated because the author didn't know the comment was carrying load-bearing information. This is a textbook example of a miscalibration: the number was changed, but its meaning — a ceiling defined by the kernel, not by the application — was not.

### Fixing RC-1 alone fixes the crash

This is the decisive test. If you change line 54 to `_EMBED_SIZE_LIMIT = 128 * 1024` (or more conservatively, `_EMBED_SIZE_LIMIT = 100 * 1024` to match the original intent), the spec-fidelity step no longer crashes. The embedded content (155.7 KB) exceeds the corrected limit, the fallback fires, `--file` flags are used, and `execve` receives a short argument. The pipeline completes.

No other single-line fix to either RC-2 or RC-3's framing yields this result. RC-2's fix requires redesigning how inputs are accumulated and checked. RC-3's fix requires replacing the entire CLI transport mechanism. RC-1's fix is one integer literal.

---

## Attack on RC-2

### RC-2 confuses a precondition with a cause

RC-2 claims that "multi-file accumulation is not modelled" — that the design assumes a single-file model and breaks when two files combine past the limit. This is factually incorrect when applied to the actual code.

The `_embed_inputs` function reads all input paths and concatenates them:

```python
def _embed_inputs(input_paths: list[Path]) -> str:
    blocks: list[str] = []
    for p in input_paths:
        content = Path(p).read_text(encoding="utf-8")
        blocks.append(f"# {p}\n```\n{content}\n```")
    return "\n\n".join(blocks)
```

The guard then checks the *total* combined embed size: `len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT`. Multi-file accumulation is modelled. The combined size is what gets checked. The design is not broken here — the combined total is correctly computed. The only broken element is the threshold against which it is compared.

RC-2 would be a valid root cause if the code were checking individual file sizes and accepting the combination without checking the total. That is not what the code does. The code checks the combined total correctly. The problem is that the threshold is wrong, not that the combination isn't measured.

### RC-2 cannot be fixed without also fixing RC-1

Suppose you accept RC-2 and add per-file size checks or tighten the accumulation logic. You would still need to decide what the maximum combined size should be. Whatever ceiling you set must be calibrated against `MAX_ARG_STRLEN`. If you set it correctly — at or below 128 KB — you have implicitly fixed the RC-1 problem. RC-2's fix subsumes RC-1's fix. This means RC-2's framing adds complexity without identifying the actual failure point: the wrong number in the constant.

### RC-2's "design assumption" claim is unfalsifiable and therefore weak

RC-2 claims the design "implicitly assumes a single-file model." Implicit assumptions are difficult to verify. The code's actual behavior is verifiable: it computes a combined total and checks it against a limit. The limit is wrong. That is a concrete, measurable defect. Attributing the failure to an "implicit design assumption" is a storytelling move, not a root cause analysis.

---

## Attack on RC-3

### RC-3 is an architectural observation, not a root cause

RC-3 argues that passing the prompt as a `-p` CLI argument creates a "hard architectural ceiling" and that no calibration of `_EMBED_SIZE_LIMIT` can fully solve the problem because the base prompt plus template will eventually hit 128 KB regardless. This is true in the abstract. It is not a root cause of this crash.

Root cause analysis requires specificity: what caused this crash, in this run, at this time? The answer is: the guard allowed 155.7 KB to be passed as a CLI argument when the OS maximum is 128 KB. The architectural choice of using `-p` is a precondition that existed before this crash occurred, before the guard was written, and before anyone cared. The guard was written *because* of the architectural choice. The guard is the mitigation. The mitigation was miscalibrated.

### RC-3's proposed fix is disproportionate and unverifiable

RC-3's implied remedy is to replace the `-p` transport with file-based or stdin-based mechanisms. This is a significant refactoring of `ClaudeProcess.build_command()`, the invocation protocol, and potentially the Claude CLI interface itself. This change cannot be verified to fix the current crash without first understanding whether the Claude CLI's `--file` flag or stdin mode actually works for large prompts. If the architecture is wrong, the fallback path (using `--file` flags) is also wrong — but the fallback path currently exists and is specifically designed to handle this case.

The fact that a `--file` fallback already exists in the codebase is evidence that the architecture is *aware* of the limitation and has provided a mitigation. RC-3 attacks the mitigation's existence rather than its miscalibration. That is the wrong target.

### RC-3 makes an unfalsifiable catastrophizing argument

"No calibration can fully solve it because the base prompt will eventually hit 128 KB." This may be true in theory. But "eventually" is not "now." The current crash is caused by a specific numeric threshold being set to a value that allows a specific payload size to pass through. Fixing the threshold fixes the crash. Whether the system will face future crashes due to prompt growth is a separate concern — a risk to be managed, not the root cause of the present failure.

RC-3 conflates "this design has limits" with "this design caused this crash." Those are not the same claim, and conflating them produces recommendations (architectural overhaul) that are wildly disproportionate to the actual defect (one wrong integer).

---

## Steelman + Refutation

### Steelman RC-2

The strongest version of RC-2: The guard was written with single-document workloads in mind. The spec-fidelity step is architecturally unique in the pipeline because it is the only step that accepts two substantial documents as inputs simultaneously (a 117.9 KB spec and a 34.2 KB roadmap). Every other step either produces output or consumes a single prior output. The multi-file accumulation model is not broken for single files; it only fails when the pipeline reaches a step whose input set was never sized for inline embedding. The design failure is that no step-level analysis was done to determine which steps could safely embed their inputs and which could not. The guard was applied uniformly to all steps when it should have been applied selectively or the per-step input budget should have been analyzed at pipeline construction time.

**Refutation**: This is a compelling framing, but it still arrives at the same root defect through a longer path. The uniform guard is only broken because its threshold is wrong. If the threshold were 100 KB, the spec-fidelity step would fall back to `--file` flags even with a single large input — the 117.9 KB spec alone exceeds 100 KB. The step-level analysis RC-2 demands would be unnecessary if the guard were correctly calibrated. RC-2's strongest form is "the guard should be more sophisticated," but that is a quality improvement, not a root cause. The crash today is caused by the number being wrong, not by the guard lacking step-level granularity.

### Steelman RC-3

The strongest version of RC-3: The `--file` fallback path is not semantically equivalent to inline embedding. When files are passed via `--file`, the Claude CLI processes them differently — potentially with different context handling, different token budgets, or different behavior in how the model sees the content. The developer who increased `_EMBED_SIZE_LIMIT` from 100 KB to 200 KB may have done so because the `--file` fallback produced worse results, not because they were unaware of OS limits. If `--file` is an inferior transport for quality reasons, then the true fix is to use a transport mechanism that can handle large payloads *and* deliver them in the inline format the model expects — which is RC-3's architectural argument.

**Refutation**: This steelman requires asserting something the evidence does not support. Nothing in the codebase, comments, or commit history (as visible from the code) suggests the threshold was raised for quality reasons rather than limit-avoidance reasons. The comment reads `# 100 KB` — if the change were intentional and quality-motivated, the developer would have updated the comment to explain the decision. The uncommented increase from `100 * 1024` to `200 * 1024` with a stale `# 100 KB` comment is the signature of an accidental or unconsidered change, not a deliberate architectural trade-off. Furthermore, even if `--file` produces marginally different model behavior, that is a quality concern — it does not cause an `OSError`. An inferior-quality successful run is categorically different from a crash. RC-3's steelman conflates quality degradation with functional failure, which are separate issues requiring separate solutions.

---

## Likelihood Scores

| Root Cause | Likelihood Score (0–100) | Reasoning |
|------------|--------------------------|-----------|
| **RC-1**: Miscalibrated `_EMBED_SIZE_LIMIT` | **78** | Direct causal link: the guard's threshold is the single control point that determined whether the fallback fired. The stale comment confirms the value was changed without understanding the OS constraint it was calibrated against. Fixing this one integer prevents the crash. |
| **RC-2**: Multi-file accumulation not modelled | **15** | The code does model combined size; the framing is partially incorrect. RC-2 is a contributing precondition (the step has an unusually large combined input set) but the combined size check exists and works correctly — only the threshold is wrong. |
| **RC-3**: CLI argument transport architectural ceiling | **7** | Architecturally valid concern for future robustness, but not a root cause of this specific crash. The fallback mechanism already exists to address the CLI ceiling; RC-3's contribution is pointing out that the fallback needs to be more reliably triggered, which is RC-1's territory. |

Scores sum to 100. RC-1 does not reach 90+ because there is a legitimate secondary observation in RC-2 (the spec-fidelity step's input profile is unusual and should have been flagged at pipeline design time), and RC-3 correctly identifies a genuine architectural debt even if it misidentifies it as a root cause.

---

## Verdict

The crash has a single proximate cause: `_EMBED_SIZE_LIMIT = 200 * 1024` allows a 155.7 KB payload to be routed into a code path that constructs a CLI argument the OS cannot accept. The guard was designed to prevent exactly this. It fails because its threshold is 56% higher than the kernel limit it was meant to enforce, a fact made apparent by the stale `# 100 KB` comment that documents the original, correct value.

RC-2 and RC-3 are not root causes — they are context and risk. RC-2 correctly observes that the spec-fidelity step has an unusual input profile that made it the first step to hit the broken guard; this is useful information for pipeline design but does not change what broke. RC-3 correctly observes that passing large payloads as CLI arguments is fragile; this is useful information for future hardening but is already addressed by the fallback mechanism, which only fails because RC-1's guard is miscalibrated.

The fix is to set `_EMBED_SIZE_LIMIT` to a value the OS can actually enforce — at or below 128 KB, and ideally at 100 KB to match the original intent and provide headroom for prompt template overhead. That fix is necessary and sufficient to prevent this crash. RC-1 is the true primary root cause.
