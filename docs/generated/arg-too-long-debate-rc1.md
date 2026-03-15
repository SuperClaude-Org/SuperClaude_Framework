# Adversarial Debate: Root Cause 1

## RC1 Hypothesis

The `_EMBED_SIZE_LIMIT` constant in `executor.py` is set to `200 * 1024` (200 KB), but the Linux kernel enforces `MAX_ARG_STRLEN` at 128 KB per argument. The guard that decides whether to embed inputs inline or fall back to `--file` flags was designed to prevent exactly this OS-level overflow. Its threshold is set 56% above the kernel limit it was supposed to protect, creating a 72 KB "dead zone" (128–200 KB) where content passes the guard, gets embedded into the `-p` CLI argument, and causes `subprocess.Popen` to crash. The stale comment `# 100 KB` alongside the `200 * 1024` value is forensic evidence that the constant was changed without understanding that its original value was calibrated against a hard OS constraint, not an application preference. The spec-fidelity step's combined input of 152.1 KB falls precisely in this dead zone, making the miscalibrated constant the direct cause of the crash.

---

## Round 1: Advocate

**RC1 IS the primary root cause.**

The causal chain is traceable to a single variable in a single line of code. Line 54 of `executor.py` sets `_EMBED_SIZE_LIMIT = 200 * 1024`. The guard on line 175 evaluates `len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT` — that is, `155.7 KB <= 200 KB` — which returns `True`, placing the combined embed into `effective_prompt`. That string is then passed as the `-p` argument to `subprocess.Popen`, which calls `execve`. The Linux kernel rejects any single argument exceeding `MAX_ARG_STRLEN` (128 KB). The result is `OSError: [Errno 7] Argument list too long`.

Every element of this chain except step 4 — the guard evaluation — is either an OS invariant or an intended design decision. The OS limit has not changed. The fallback mechanism (using `--file` flags) exists and is correct. The only control point that determined whether the fallback fired is the threshold, and the threshold is wrong.

The decisive test of any root cause hypothesis is: does fixing it alone fix the crash? Changing `_EMBED_SIZE_LIMIT = 200 * 1024` to `_EMBED_SIZE_LIMIT = 100 * 1024` (matching the original commented intent) means the guard evaluates `155.7 KB <= 100 KB` as `False`. The fallback branch executes. `--file` flags are passed. `execve` receives a short argument. No crash. That is a one-line fix that is both necessary and sufficient for this failure.

The stale comment is not incidental. The comment `# 100 KB` documents the original, correct value. The fact that the comment was not updated when the value was changed is the signature of an accidental or unconsidered modification — someone raised the number, possibly to silence over-triggering of the fallback, without recognizing that the number was not an arbitrary application preference but a threshold derived from a kernel constant. The guard had a purpose; the change undermined it silently.

---

## Round 1: Critic

**RC1 is a contributing factor but NOT the primary root cause.**

Lowering `_EMBED_SIZE_LIMIT` to 120 KB prevents this specific crash in this specific run. It does not fix the underlying architectural problem, and characterizing it as the primary root cause misdiagnoses the system's actual failure mode.

The primary root cause is architectural: the system passes the full prompt — including all embedded file content — as a single CLI argument via the `-p` flag. This is the wrong transport mechanism for variable-sized content. The Linux kernel's `MAX_ARG_STRLEN` is 128 KB. The sum of prompt template overhead plus any non-trivial spec file will approach this limit regardless of where `_EMBED_SIZE_LIMIT` is set. A constant miscalibration is a symptom of this architectural mismatch, not its cause.

Consider the evidence from `arg-too-long-root-causes.md` (RC3): even if `_EMBED_SIZE_LIMIT` were corrected to 100 KB, a spec file at 117.9 KB alone exceeds that limit. The extract step, which also receives `config.spec_file` as an input, would also be at risk as spec files grow. The guard would trigger the fallback, but the fallback itself is misunderstood: it switches `step.inputs` to `--file` flags but `effective_prompt` (the step's own prompt string) is still passed via `-p`. For steps where the prompt itself is large, the fallback provides no protection.

The root cause, properly stated, is that the system has no principled solution for the OS argument length constraint. `_EMBED_SIZE_LIMIT` is one miscalibrated manifestation of an unprincipled attempt to patch around a constraint the architecture never correctly modelled. Fixing the constant treats the symptom; it does not treat the disease.

---

## Round 2: Advocate

**The Critic conflates future risk with present cause.**

The Critic's argument has two components: (1) `_EMBED_SIZE_LIMIT` is just one manifestation of a deeper architectural problem, and (2) even a corrected constant would not fully solve the problem because spec files above 100 KB would still fail. Both observations are true in the abstract. Neither makes RC1 less than the primary cause of this crash.

Root cause analysis answers a specific question: what caused this failure in this run? The answer is not "the architecture chose CLI arguments as a transport." That choice predates this pipeline, was present during every successful run, and was specifically mitigated by the fallback mechanism. The answer is not "spec files can grow beyond safe limits." That is a risk observation, not a cause of the failure that occurred. The answer is: the guard that was supposed to prevent an OS argument overflow was set to a value that allowed a 152.1 KB payload through. That is the only element in the causal chain that changed or was misconfigured.

The Critic's claim that "even a corrected constant would not fix the problem because a 117.9 KB spec file alone would exceed 100 KB" actually strengthens RC1. If `_EMBED_SIZE_LIMIT = 100 * 1024`, the guard evaluates `152.1 KB <= 100 KB` as `False`. The fallback fires. The system does not pass the spec content as a `-p` argument at all — it uses `--file` flags for the inputs. That is the correct behavior. The spec file does not become part of the `-p` argument in the fallback path; `effective_prompt` is set to `step.prompt` (the template only, approximately 4 KB). The crash does not occur. The Critic appears to be conflating the inline-embed path with the fallback path.

The architectural concern (RC3's domain) is legitimate for future hardening. It is not an explanation of this crash.

---

## Round 2: Critic

**The Advocate's defense of the fallback path is partially correct but does not close the gap.**

The Advocate is right that the fallback sets `effective_prompt = step.prompt` (template only), not the full embedded string. This narrows the Critic's RC3 argument. The fallback does handle the OS constraint adequately for the current step's prompt size. The Advocate is correct that a corrected `_EMBED_SIZE_LIMIT` would prevent this specific crash at spec-fidelity.

However, the Critic's core position stands: RC1 is a miscalibrated constant, and miscalibrated constants are symptoms, not primary causes. The question is not whether fixing line 54 prevents the crash — it does. The question is what causal level is most explanatory and most actionable for the system as a whole.

The primary root cause should identify the failure in reasoning or process that produced the defect. A constant set to 200 KB when it should be 100 KB is the output of a reasoning failure: the developer who changed the value did not understand — or did not check — that `_EMBED_SIZE_LIMIT` was calibrated against `MAX_ARG_STRLEN`, not against context window preferences. That reasoning failure is: "the system has no documented or enforced relationship between `_EMBED_SIZE_LIMIT` and the OS constraint it proxies." The root cause, at the process level, is the absence of a constraint derivation — the constant is magic rather than computed from `MAX_ARG_STRLEN` with a safety margin.

This means the real fix is not `200 * 1024` → `100 * 1024` but rather `_EMBED_SIZE_LIMIT = int(MAX_ARG_STRLEN * 0.75)` with `MAX_ARG_STRLEN` as a named constant. That fix encodes the reasoning, not just the number. RC1 identifies the wrong constant; it does not identify why the constant is wrong or what process produces the correct one. A deeper root cause would prevent recurrence, not just fix the current value.

---

## Verdict

**Likelihood RC1 is primary root cause**: 72

**Reasoning**: RC1 has a direct, unambiguous causal link to the crash — the miscalibrated constant is the single control point that determined whether the fallback fired, and changing it alone prevents the failure. The score does not reach the high eighties because the Critic correctly observes that RC1 identifies a symptom (a wrong number) rather than the underlying failure mode (no enforced derivation of the constant from the OS limit it proxies), and a recurrence-proof fix requires encoding the relationship to `MAX_ARG_STRLEN`, not just correcting the current value.
