# Adversarial Debate: Root Cause 2

## RC2 Hypothesis

The `spec-fidelity` step is structurally unique in the pipeline because it embeds the raw
user-supplied spec file (`config.spec_file`) as a direct input alongside a pipeline-generated
artifact (`roadmap.md`). Every other step embeds only pipeline-generated outputs, whose sizes
are implicitly bounded by prior Claude outputs. The spec file is unbounded — it grows with user
content. The v2.25 spec at 117.9 KB alone consumes 92% of `MAX_ARG_STRLEN` (128 KB) before
`roadmap.md` (34.2 KB) is added. The combined 152.1 KB passes the miscalibrated guard
(`_EMBED_SIZE_LIMIT = 200 KB`) and crashes the OS argument list. The system has no per-file size
check before `_embed_inputs()` constructs the combined payload. RC2 contends that this
architectural uniqueness — user-controlled, unbounded input at a specific step — is the primary
root cause, not a miscalibrated constant or a transport mechanism limitation.

---

## Round 1: Advocate

**RC2 IS the primary root cause.**

The crash has a clear structural precipitant: the `spec-fidelity` step is the only step that
injects an artifact whose size is not bounded by any prior pipeline stage. Every other step in
the v5 pipeline consumes Claude outputs — extraction, debate transcripts, roadmap variants. These
are bounded by the model's output behavior. The spec file is bounded only by the user's content.
When the user's spec grows from 30 KB (cross-framework, working) to 117.9 KB (v2.25, failing),
no other step changes behavior — only `spec-fidelity` and `extract` are exposed to this growth.

This architectural uniqueness is the primary causal factor because it is the variable that
changed between the working run and the failing run. The pipeline is identical. The constant
`_EMBED_SIZE_LIMIT` is identical. The only difference is the size of the user-supplied spec file.
That means the spec file size is the independent variable, and the failure is the dependent
variable. By definition, the architectural decision to embed an unbounded user file at this step
is the primary root cause.

The absence of any per-file size check before `_embed_inputs()` amplifies this. The code has no
mechanism to ask: "Is any single input file already too large to safely combine with another?" At
117.9 KB, the spec file alone is 92% of `MAX_ARG_STRLEN`. Adding any second file of meaningful
size — even a small 10 KB fragment — would push the combined total past the OS limit. The design
assumes accumulation is safe as long as the total passes the guard. That assumption is broken the
moment one file alone occupies nearly the full budget.

---

## Round 1: Critic

**RC2 is a contributing factor, not the primary root cause.**

The Advocate's argument conflates "the variable that changed" with "the root cause." These are
not the same. If I remove a fuse from a circuit and the lights go out, the fuse removal is the
immediate trigger — but if the fuse was rated too low for the circuit's design load, the
undersized fuse is the root cause. The same logic applies here.

The `_EMBED_SIZE_LIMIT` constant is set to 200 KB — 56% above the actual OS constraint of 128 KB.
The guard was specifically designed to prevent this class of OS failure. It failed at its
designed purpose because it was miscalibrated. If `_EMBED_SIZE_LIMIT` had been set to 100 KB (as
the comment in the code originally indicated), the combined 152.1 KB embed would have exceeded
the guard and triggered the `--file` fallback. The crash would not have occurred. The spec file
could have been 200 KB and the pipeline would have routed correctly.

RC2's "architectural uniqueness" observation is accurate but it proves too much. Any pipeline
step could fail if its aggregate inputs grow. The extract step already failed against a larger
version of this same spec before it was condensed — and extract embeds only one file. That
failure was also caused by the miscalibrated constant (a single 120+ KB file passing a 200 KB
guard). Fixing the constant would have prevented both crashes without requiring any architectural
change to which steps embed which files. RC2 describes a symptom of RC1, not a cause independent
of it.

Furthermore, the Advocate's claim that the spec file is "unbounded" while pipeline artifacts are
"bounded" overstates the distinction. A debate transcript for a 50-step pipeline with deep
analysis could easily reach 80+ KB. Extraction of a large spec could produce 50 KB. These are not
hard bounds — they are soft expectations. The real issue is that no step has a correct guard, not
that one step has a uniquely unbounded input.

---

## Round 2: Advocate

**The Critic's RC1 rebuttal misidentifies what the constant is actually guarding.**

The Critic argues: fix `_EMBED_SIZE_LIMIT` to 100 KB and the crash is prevented. This is
arithmetically correct for this specific incident. It does not hold as a general solution.

Consider the guard logic at the call site:

```python
embedded = _embed_inputs(step.inputs)
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded
```

The guard checks the *embedded portion only*, not the full `-p` argument. The `step.prompt`
template (approximately 3-5 KB) is added after the check passes. This means even a correctly
calibrated guard of 100 KB leaves the system in a state where `effective_prompt` can slightly
exceed `MAX_ARG_STRLEN` if the template grows. More importantly, a guard of 100 KB would mean
that two files of 55 KB each (110 KB combined) exceed the guard and fall back to `--file` — even
though individually and combined they are well within the OS limit. The guard would be over-
conservative because it has no per-file awareness.

The Critic also invokes the extract step's earlier failure as evidence that RC1 explains both
crashes. But the extract step embeds a *single* file. A per-file size check would catch that case
directly: "this file is 120+ KB, exceeding the per-file budget, route to --file." The same fix
applies to both steps. That fix is RC2's recommended correction — add accumulation-aware, per-file
budget logic — not merely adjusting the constant.

Lastly, the Critic's claim that pipeline artifacts are not truly bounded is a red herring. The
point is not that they are mathematically bounded; it is that their sizes are correlated with
prior Claude outputs, which are subject to context window limits and instruction constraints.
A user spec file is subject to none of these. The v2.25 spec grew from 30 KB to 117.9 KB between
runs purely due to user content decisions. That 4x growth with no pipeline signal is the
structural risk RC2 identifies.

---

## Round 2: Critic

**The Advocate's rebuttal shows RC2 and RC1 are not separable — which undermines RC2's primacy.**

The Advocate's observation that the guard checks `embedded` alone rather than
`step.prompt + embedded` is correct and is a real deficiency. But this observation strengthens
RC1 and RC3 simultaneously: it means the constant is doubly miscalibrated — wrong threshold *and*
wrong thing being measured. Neither of these is the accumulation model flaw RC2 describes. Both
are failures of the guard's design and placement.

The Advocate's per-file check proposal is reasonable, but it is a solution, not a root cause
identification. The question is: *why* did the system fail? It failed because a guard that was
designed to intercept OS-constraint violations had its threshold set above the OS limit. The
per-file check is a better guard design. RC1 is the diagnosis that the guard was wrong.

Consider the counterfactual chain: if `_EMBED_SIZE_LIMIT` were 64 KB — well below
`MAX_ARG_STRLEN` with conservative headroom — then even a 117.9 KB spec file alone would trigger
the fallback before any second file is added. The spec file's "architectural uniqueness" never
becomes relevant because the guard fires first. RC2's mechanism (accumulation without per-file
awareness) never gets the chance to produce a dangerous total, because the first file already
exceeds the conservative guard. This means RC1 is the true gating condition.

The Advocate is correct that the constant will be changed again and that a design dependent on a
single correctly-calibrated constant is fragile. But this argues for a better RC1 fix (multiple
guards, defensive margins, test coverage of the constant) rather than elevating RC2 to primacy.
RC2 describes a real design gap. It is not the primary cause of this specific crash, because a
correct RC1 fix would have prevented the crash regardless of RC2's presence.

---

## Verdict

**Likelihood RC2 is primary root cause**: 45

**Reasoning**: RC2 correctly identifies the structural uniqueness of the spec-fidelity step and
the absence of per-file size awareness as a real and exploitable design gap — the spec file's
unbounded growth is the independent variable that caused the working run to fail on the second
run. However, RC1 (miscalibrated `_EMBED_SIZE_LIMIT` set 56% above the actual OS constraint) is
a more direct causal antecedent: a correctly calibrated constant would have intercepted the 152.1
KB embed before it reached `Popen`, regardless of accumulation model design. RC2 is the better
design diagnosis and points to the more durable fix, but RC1 is the more proximate cause of this
specific crash — making RC2 a strong contributing factor at roughly equal weight rather than the
clear primary root cause.
