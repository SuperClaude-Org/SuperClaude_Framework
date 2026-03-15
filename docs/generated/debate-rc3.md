# Adversarial Debate: RC-3 as the True Root Cause

**Position assigned**: RC-3 — Passing the prompt as a CLI argument (`-p <text>`) is the fundamental architectural root cause of the `OSError: [Errno 7] Argument list too long` crash.

---

## Position Statement

The crash at the `spec-fidelity` step is not primarily a calibration error (RC-1) nor a multi-file accumulation oversight (RC-2). It is the direct consequence of an architectural decision: embedding a large, variable-length payload into a CLI argument. That decision places the system permanently beneath a hard kernel ceiling — 128 KB per argument (`MAX_ARG_STRLEN`) — that no amount of constant-tuning or per-file accounting can eliminate. RC-1 and RC-2 are downstream symptoms of RC-3. They describe specific configurations under which the architectural flaw is exposed, but they do not describe the flaw itself. Fix the architecture and RC-1 and RC-2 become irrelevant. Leave the architecture intact and you have an indefinitely fragile system that will crash again on the next large step.

---

## Argument for RC-3

### The causal chain

The crash has a direct, traceable causal chain:

1. `process.py::build_command` passes the full prompt string as the value of the `-p` flag.
2. The Linux kernel's `execve` syscall enforces `MAX_ARG_STRLEN = 128 KB` per individual argument.
3. The combined prompt for the `spec-fidelity` step is 155.7 KB.
4. 155.7 KB > 128 KB. The kernel rejects the `execve` call with `ENOMEM` / `E2BIG`, surfaced as `OSError: [Errno 7]`.

Every other fact in this case — the miscalibrated constant, the multi-file combination — is an explanation of *why* the payload reached 155.7 KB, not an explanation of *why* 155.7 KB is fatal. The fatality comes entirely from the architectural choice to pass that payload as a CLI argument.

### The hard ceiling is non-negotiable

`MAX_ARG_STRLEN` is a compile-time kernel constant. It is not configurable per-process, per-user, or per-application. It cannot be overridden by the Claude CLI, by `executor.py`, or by any userspace code in this stack. It is the same 128 KB on every standard Linux host the pipeline will ever run on. This is categorically different from the guard in `executor.py`, which is a policy decision and can be changed. A policy mismatch (RC-1) is a bug. An architectural constraint (RC-3) is a wall.

### Prompt content is inherently unbounded

The embedded prompt is constructed from two variable-length sources: the step's base prompt template and the embedded inputs. As the project evolves, either or both of these will grow. A roadmap pipeline by definition operates on large specification documents. The `spec-fidelity` step's job is to compare a 117.9 KB spec against a 34.2 KB roadmap — this is not an edge case, it is the nominal workload. Any architecture that cannot handle nominal workloads without crashing is architecturally broken.

### The existing fallback proves the correct fix is already known

`executor.py` already implements a file-based fallback for input files:

```python
extra_args = ["--file", str(path) for path in step.inputs]
```

The developers already recognized that embedding large inputs as CLI argument text is unsafe. They built a fallback that routes large inputs through `--file` flags instead. But this fallback applies only to `step.inputs`, not to the composed `effective_prompt`. The prompt itself — which is what crashes — is always passed via `-p`. The fix for inputs was applied correctly but was never extended to the final assembled prompt. RC-3 is the identification of that gap. The code already gestures at the solution; it just doesn't apply it to the right thing.

### What happens if only RC-1 is fixed

If `_EMBED_SIZE_LIMIT` is corrected from 200 KB to something below 128 KB (say, 100 KB), the current 155.7 KB payload would trigger the fallback. The *current* `spec-fidelity` step would stop crashing. But:

- The base prompt template itself could grow past 128 KB independently of any embedded inputs, and no guard anywhere catches that.
- A step with a 90 KB base prompt + 40 KB of embedded content = 130 KB would still crash, because 130 KB > 128 KB and the guard would allow it (90 KB + 40 KB < 128 KB if measured incorrectly, or 130 KB total if measured correctly but still below a 200 KB guard).
- More concretely: the fallback routes *inputs* via `--file`, but the *prompt* is still passed as `-p`. If the step's base prompt template alone exceeds 128 KB, the fallback does nothing — the prompt is still a CLI argument, still subject to `MAX_ARG_STRLEN`.

Fixing RC-1 is playing whack-a-mole with a kernel constraint. Every future step that pushes the combined prompt past 128 KB will crash.

### What happens if only RC-2 is fixed

If per-file size checks are added so that the embed is rejected whenever any single input or any combination of inputs exceeds a threshold, the `spec-fidelity` step is again guarded for its *current* payload. But:

- The prompt template is not an "input file." It is not covered by per-file checks.
- Future steps with large prompt templates but small inputs would bypass all file-based guards and crash.
- The fallback still passes the prompt via `-p`, so the ceiling on prompt size is still 128 KB, enforced by the kernel, not by application code.

RC-2, if fixed in isolation, makes the system slightly more robust against one specific failure pattern — multi-file accumulation crossing a threshold — while leaving the architecture fully capable of crashing in any other scenario that drives the prompt past 128 KB.

---

## Attack on RC-1

### The constant is wrong, but that is a symptom not a disease

RC-1 correctly identifies that `_EMBED_SIZE_LIMIT = 200 * 1024` is set above the OS limit and that the code comment says `# 100 KB` while the value is 200 KB. This is clearly a maintenance error — the constant was changed at some point without understanding the OS constraint it enforces. But calling this the "root cause" confuses a proximate trigger with a structural vulnerability.

### Fixing the constant does not fix the architecture

Suppose `_EMBED_SIZE_LIMIT` is corrected to `100 * 1024` (102 KB). The current 155.7 KB payload triggers the fallback. The `spec-fidelity` step no longer crashes today. What has actually been fixed? The guard now intercepts combined prompt + inputs above 100 KB and routes inputs via `--file`. But the prompt itself is still passed as `-p`. The guard is measuring the combined payload to decide whether to offload inputs, but it is offloading the wrong thing. The inputs are offloaded; the prompt remains as a CLI argument.

If the base prompt template for any step exceeds 100 KB on its own — before any inputs are embedded — the guard does not trigger the fallback (there is nothing to embed), and the prompt still crashes `execve`. The guard's decision logic is:

```python
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
```

`embedded` is only the input content. If `embedded` is empty or small but the base prompt is huge, this condition evaluates `True` (small embedded ≤ limit), appends the small embedded to the large prompt, and passes the entire large prompt via `-p`. The guard is structurally incapable of protecting against a large base prompt because it does not measure the base prompt.

### The comment/constant mismatch is evidence of confusion, not a fix target

The `# 100 KB` comment with a `200 * 1024` value does show the constant was changed carelessly. But correcting the constant to match the comment would set it to 100 KB — which is still not 128 KB, still not the actual OS limit. If RC-1 advocates want the constant to correctly reflect the OS constraint, the value should be 128 KB, not 100 KB. The comment is unreliable as a specification. And even if the constant is set to exactly 128 KB, that is still only a runtime guard against a specific measurement of a specific variable. It does not change the architectural fact that `-p` has a hard kernel ceiling.

---

## Attack on RC-2

### Multi-file accumulation is a specific instance of a general problem

RC-2 argues that the real issue is that no code models the combined size of multiple inputs. This is true as a description of how the threshold was crossed in this specific case. But it is not a general explanation of the failure mode. The crash does not care how the 155.7 KB was assembled. It cares only that a single CLI argument is 155.7 KB. Whether that value came from two files, ten files, or a single enormous prompt template is irrelevant to the kernel.

### Per-file checks cannot cover the full attack surface

If RC-2's fix is to check each file's size individually before including it in the embed, the check would look something like:

```python
if file_size > some_threshold:
    use_file_flag(file)
else:
    embed(file)
```

This prevents a single large file from being embedded. But:

- Two 70 KB files are each below any reasonable per-file threshold, but together produce a 140 KB embed that exceeds `MAX_ARG_STRLEN`. RC-2 correctly identifies this gap but its own proposed fix (per-file checks) does not close it — you need a combined-size check.
- A combined-size check could work, but it must account for the base prompt size as well. If the base prompt is 80 KB and you allow up to 48 KB of combined inputs (total = 128 KB), you need to know the base prompt size at the point of decision. The current code does not pass base prompt size to `_embed_inputs`. This is solvable, but it means the fix is more invasive than RC-2 suggests.
- Even a correct combined-size check that accounts for base prompt size does not eliminate the architectural fragility. It adds a guardrail but the guardrail is in userspace, enforcing a kernel constraint that the kernel will enforce anyway if the guardrail fails or is misapplied.

### RC-2's proposed fix still leaves the prompt as a CLI argument

RC-2, properly implemented, would prevent multi-file accumulation from crossing the OS limit. But it does not change the fact that the final prompt is passed via `-p`. Any future change to the system — a longer base prompt template, a new step type, a different use of the pipeline — could push the prompt past 128 KB without triggering any file-size check. The architectural ceiling remains.

---

## Steelman + Refutation

### Steelman of RC-1

RC-1's strongest form: "The guard is the *only* mechanism the system uses to prevent OS-level failures. If it were correctly calibrated, it would have triggered the fallback and the crash would not have occurred. The fallback mechanism works — it routes inputs via `--file`. The guard is the sole line of defense and it is miscalibrated. Fix the guard and the crash is prevented." This is compelling because it is operationally true: a correctly calibrated guard at ≤128 KB would have triggered the fallback for the current 155.7 KB payload, and the fallback does avoid passing inputs as CLI text. The guard is the most directly responsible broken component.

**Refutation**: The fallback routes *inputs* via `--file` but the *prompt* itself is still passed via `-p`. A correctly calibrated guard at 128 KB would have measured the combined embed (155.7 KB > 128 KB), triggered the fallback, and passed inputs via `--file` — but the step's base prompt (whatever it is, minus the embedded inputs) would still be passed via `-p`. If the base prompt template alone is, say, 50 KB, then after the fallback the `-p` argument is 50 KB, which is fine. But this only works because the base prompt template happens to be small enough. The guard is not measuring prompt template size. The fix is correct for the current case but brittle in general. More fundamentally: the fallback was designed to handle large inputs, not large prompts. Applying the correct constant to a guard that doesn't measure the right thing is a partial fix at best.

### Steelman of RC-2

RC-2's strongest form: "The spec-fidelity step has two inputs that are individually within safe bounds (117.9 KB and 34.2 KB). Any per-input guard would pass them. The system fails because no code models the *combination*. This is a software design oversight independent of the constant value: even if `_EMBED_SIZE_LIMIT` were 100 KB, two 60 KB files would each pass individual checks, combine to 120 KB, and exceed `MAX_ARG_STRLEN`. The fix must include combination-aware logic." This is the strongest version of RC-2 because it identifies a genuine algorithmic gap that RC-1 does not address.

**Refutation**: The combination-aware logic RC-2 prescribes must be anchored to the OS limit to be correct. To anchor correctly to the OS limit, you must know what the OS limit is. RC-2 therefore implicitly depends on RC-1 being fixed — the combination threshold must be ≤128 KB. But the deeper issue is that even correct combination-aware logic measuring against 128 KB does not change the architecture: the prompt is still `-p <text>`, the kernel still enforces `MAX_ARG_STRLEN`, and any configuration of base prompt + embedded content that exceeds 128 KB will crash. RC-2 narrows the surface area of the vulnerability; it does not eliminate it. The correct architectural fix is to stop treating 128 KB as a constraint to route around via application-level guards, and instead use a mechanism (stdin, prompt file, temp file) that has no such constraint.

---

## Likelihood Scores

| Root Cause | Likelihood Score (0-100) | Reasoning |
|---|---|---|
| RC-1 (miscalibrated constant) | 25 | Directly responsible for *this specific crash* not being caught by the guard. Fixing it prevents the current failure but leaves the architectural fragility intact. It is the proximate failure of the defense layer, not the reason the defense layer is needed. |
| RC-2 (multi-file accumulation not modelled) | 20 | Correctly describes how the threshold was crossed in this instance. However, it is a specific case of the general problem that any sufficiently large prompt passed via `-p` will crash. Fixing RC-2 addresses one input pattern without addressing the root constraint. |
| RC-3 (prompt passed as CLI argument) | 55 | The hard kernel constraint `MAX_ARG_STRLEN` is the ceiling that makes RC-1 and RC-2 failures possible. Without passing the prompt as a CLI argument, neither RC-1 nor RC-2 would matter. The existing fallback for inputs already demonstrates the correct pattern; extending it to the prompt eliminates the failure mode entirely. |

Note: Scores do not sum to 100 because root causes are not mutually exclusive — all three contributed to the crash. The scores reflect which cause is most "primary" in the sense that fixing it alone provides the most durable protection.

---

## Verdict

RC-3 is the primary root cause.

The argument is structural. `MAX_ARG_STRLEN = 128 KB` is a hard kernel constraint that cannot be negotiated. Passing any variable-length payload as a CLI argument means the system is permanently vulnerable to that payload exceeding 128 KB. The fact that it exceeded 128 KB in this case due to a miscalibrated guard (RC-1) and multi-file accumulation (RC-2) explains the triggering conditions but not the underlying vulnerability.

The clinching evidence is the existing fallback. The codebase already contains code that says: "if the payload is too large to pass as CLI argument text, use file-based alternatives instead." That code applies this wisdom to `step.inputs` but not to the final assembled prompt. The developers understood the problem in one dimension and solved it there. RC-3 is the identification that the solution was applied incompletely.

The correct fix is one of:
1. Write the full composed prompt to a temporary file and pass `--file <tempfile>` instead of `-p <text>`.
2. Pass the prompt via stdin rather than as a CLI argument.
3. Use the Claude SDK's programmatic API, which does not involve `execve` and has no `MAX_ARG_STRLEN` constraint.

Any of these eliminates the architectural ceiling. RC-1 and RC-2 are then reduced to calibration notes — useful for defense-in-depth but no longer load-bearing.

RC-1 and RC-2 describe why the system crashed today. RC-3 describes why the system was always going to crash eventually.
