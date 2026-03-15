# Adversarial Debate: Root Cause 3

## RC3 Hypothesis

The `OSError: [Errno 7] Argument list too long` crash is not primarily a calibration error or an input-size accounting failure. It is the direct consequence of a fundamental architectural decision: the pipeline passes the full composed prompt — including all embedded content — as the value of the `-p` flag to the `claude` CLI. The OS kernel enforces `MAX_ARG_STRLEN = 128 KB` per CLI argument, a compile-time constant that no userspace code can override. `_EMBED_SIZE_LIMIT` was introduced as a context-window proxy (set at 200 KB) and was never calibrated against the OS constraint. The fallback mechanism at `executor.py:184-188` routes `step.inputs` through `--file` flags when the embedded content is large, but the fallback does not route the prompt itself differently — `effective_prompt` is always passed as `-p`. Because the prompt IS the embedded content, the fallback cannot rescue a large prompt from the OS constraint. The correct fix is architectural: prompts above a byte threshold must be written to temp files and passed via stdin or `--file`, not via `-p`.

---

## Round 1: Advocate

**RC3 is the primary root cause because the architectural ceiling is non-negotiable and the fallback is structurally incapable of preventing the crash.**

The causal chain for this failure runs: `build_command()` assembles `-p <effective_prompt>` → `execve` receives a 155.7 KB argument → the Linux kernel enforces `MAX_ARG_STRLEN = 128 KB` per argument → the kernel rejects the call with `ENOMEM` / `E2BIG` → Python surfaces `OSError: [Errno 7]`. The only link in that chain that cannot be patched by a constant change or a size check is the second-to-last one: the kernel constraint is a compile-time kernel constant, not a policy. It is 128 KB on every standard Linux host, forever.

RC1 (miscalibrated constant) and RC2 (multi-file accumulation not modelled) explain how the payload reached 155.7 KB. RC3 explains why 155.7 KB is fatal. Those are categorically different explanations. Fix RC1 or RC2 and the current step stops crashing today. Fix RC3 and the entire class of prompt-too-large failures is eliminated, permanently.

The existing fallback code provides the clearest evidence. The developers already understood that large content must not be passed as a CLI argument — they built `--file` routing for `step.inputs`. That insight was correct and the implementation was correct for inputs. It was simply never extended to `effective_prompt`. RC3 is the identification of that exact gap: the correct architectural pattern exists in the codebase but is applied to the wrong object. The fix is to extend it to the prompt.

---

## Round 1: Critic

**RC3 accurately describes an architectural weakness but conflates a design observation with a causal diagnosis. The primary root cause of this specific crash is the miscalibrated constant, not the architectural pattern.**

A root cause is the earliest preventable event in the causal chain whose correction would have prevented the failure. By that definition, RC1 is the primary root cause. The fallback mechanism at `executor.py:184-188` was designed precisely to prevent prompts from exceeding OS limits. Had `_EMBED_SIZE_LIMIT` been set correctly — at or below 128 KB — the combined 155.7 KB payload would have triggered the fallback, inputs would have been passed via `--file`, and the composed `effective_prompt` would have been the base prompt template only, well under 128 KB. The crash would not have occurred.

RC3's claim that "the fallback cannot rescue large prompts" is technically correct in one specific scenario — a base prompt template that alone exceeds 128 KB — but that is not what happened here. The base prompt template for `spec-fidelity` is not 128 KB; it is the embedded 117.9 KB spec plus 34.2 KB roadmap that pushed the combined prompt over the limit. The fallback, had it been triggered, would have routed those inputs via `--file` and the `-p` argument would have been only the base template. RC3 argues from a hypothetical failure mode (huge base template) rather than the actual failure mode (huge combined embed).

Calling the architectural pattern the primary root cause when there is a functioning guard that simply has the wrong threshold is category confusion: it elevates a long-term design concern to the status of the immediate causal agent.

---

## Round 2: Advocate

**The critic's "fallback would have worked" argument assumes the fallback measures the right thing. It does not.**

The critic's argument depends on a critical assumption: that after the fallback fires, the `-p` argument shrinks to just the base prompt template, which is safely under 128 KB. This is correct for the current `spec-fidelity` step — but only because the base template happens to be small. The guard at `executor.py:175` measures `len(embedded.encode("utf-8"))`, where `embedded` is the concatenated content of `step.inputs`. It does not measure the base prompt size. It does not measure the total size of `effective_prompt` that will be passed as `-p`.

This means the guard has a structural blind spot: if the base prompt template alone is, say, 130 KB, the guard sees `embedded` as empty (no inputs to embed), evaluates `len("".encode("utf-8")) = 0 <= _EMBED_SIZE_LIMIT`, and passes the 130 KB base template directly as `-p` with no fallback. The OS crashes the call. No constant correction prevents this. The guard is not protecting the right variable.

More broadly: the critic's position requires believing that the correct fix is to tune a threshold in a guard that measures the wrong thing. That is not a fix — it is a guard that happens to prevent the current failure while remaining structurally incapable of preventing the general class. A guard that cannot protect against the general case is not a defense; it is luck. The architectural fix eliminates the class entirely by removing the dependency on `MAX_ARG_STRLEN` for prompt delivery.

---

## Round 2: Critic

**RC3 is a valid architectural recommendation but its scope disqualifies it as the primary root cause of this specific failure.**

The advocate has now shifted the argument from "the fallback is broken for this failure" to "the fallback is broken for a hypothetical future failure involving a large base template." That is a legitimate architectural concern, but it is not the root cause of the crash that actually occurred. Root cause analysis is about what caused this failure, not what could cause a different failure in a different scenario.

For the failure that actually occurred — `spec-fidelity` step, 155.7 KB combined prompt from two embedded files — the causal sequence is: `_EMBED_SIZE_LIMIT` was 200 KB → combined embed was 155.7 KB → 155.7 KB < 200 KB so the guard did not trigger → the full 155.7 KB prompt was passed as `-p` → the OS rejected it. Change `_EMBED_SIZE_LIMIT` to any value below 155.7 KB and this specific crash does not happen.

The advocate is correct that the fallback does not measure the base prompt size and that a large base template could crash even with a correct constant. But "could crash" is not "did crash." Root cause analysis must be grounded in the actual failure path, not in the space of possible future failures. RC3 is better classified as an architectural debt item and a defense-in-depth improvement than as the primary root cause of the crash under investigation. The correct engineering response is: fix RC1 to stop this crash, then address RC3 as a follow-on architectural hardening task.

---

## Verdict

**Likelihood RC3 is primary root cause**: 38

**Reasoning**: RC3 correctly identifies the most durable fix and the deepest structural vulnerability — passing variable-length prompts as CLI arguments creates an OS-imposed ceiling that no application-level guard can fully eliminate — but "primary root cause" requires being the earliest preventable event specific to this failure, and that distinction belongs to the miscalibrated constant (RC1), which is the direct reason the existing guard failed to intercept the oversized payload. RC3 is a genuine architectural flaw and the correct long-term remediation target, but it is more accurately categorized as a latent systemic vulnerability that RC1's miscalibration exposed, rather than the discrete causal agent responsible for this specific crash.
