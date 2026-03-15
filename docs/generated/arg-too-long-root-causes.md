# Root Cause Analysis: OSError [Errno 7] at spec-fidelity Step

**Issue**: `OSError: [Errno 7] Argument list too long: 'claude'`  
**Step**: `spec-fidelity` (step 9 in the v5 pipeline)  
**Context**: Failure occurs after merge and test-strategy both pass successfully  
**Date**: 2026-03-14

---

## Evidence Summary

| Artifact | Size |
|----------|------|
| `v2.25-spec-merged.md` (spec_file) | 117.9 KB |
| `roadmap.md` (merge output) | 34.2 KB |
| **Combined spec-fidelity inputs** | **152.1 KB** |
| `extraction.md` | 35.3 KB |
| test-strategy inputs (roadmap + extraction) | 69.5 KB ← **PASSED** |
| `_EMBED_SIZE_LIMIT` constant | 200 KB |
| `MAX_ARG_STRLEN` kernel limit | 128 KB |

**Key mechanism**: `roadmap_run_step()` in `executor.py` calls `_embed_inputs()` which reads
all input files into a single string. If `len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT`
(200 KB), the combined content is appended to the prompt string and passed as the `-p` argument
to the `claude` subprocess via `subprocess.Popen`. The Linux kernel enforces `MAX_ARG_STRLEN`
(128 KB) as a hard limit on any single argument. The 152.1 KB combined embed exceeds this limit.

test-strategy passed (69.5 KB inputs). spec-fidelity fails (152.1 KB inputs). The
`v2.25-spec-merged.md` at 117.9 KB is the critical variable — it is unique to the spec-fidelity
step as an input.

---

## Root Cause 1: `_EMBED_SIZE_LIMIT` Is Set Above `MAX_ARG_STRLEN`

**Hypothesis**: The embed guard (`_EMBED_SIZE_LIMIT = 200 * 1024` = 200 KB) is calibrated
against a different constraint than the actual OS limit it is supposed to protect. The constant
comment even acknowledges the discrepancy: `# 100 KB` (the comment says 100 KB; the value is
200 KB). The intended protection threshold should have been set below `MAX_ARG_STRLEN` (128 KB),
but the constant was set 56% above it. Any step whose combined inputs exceed 128 KB but stay
under 200 KB will pass the guard, embed successfully, then crash at `Popen`.

**Evidence**:
- `_EMBED_SIZE_LIMIT = 200 * 1024` at `executor.py:54`
- Comment reads `# 100 KB` — mismatch suggests the limit was changed without updating the guard logic
- spec-fidelity combined inputs: 152.1 KB — above 128 KB, below 200 KB (falls exactly in the gap)
- The fallback path (using `--file` flags instead of embedding) is only triggered at > 200 KB

**Likelihood assessment**: To be determined by adversarial debate.

---

## Root Cause 2: spec-fidelity Is the Only Step That Embeds the Raw Spec File

**Hypothesis**: Every other pipeline step embeds pipeline-generated artifacts (extraction,
roadmap variants, diff, debate) whose sizes are bounded by Claude's output behavior. The
spec-fidelity step is structurally unique: it embeds `config.spec_file` — the original input
file supplied by the user — whose size is unbounded and user-controlled. As spec files grow
(the v2.25 spec is 117.9 KB, up from ~30 KB for the working cross-framework spec), no step
other than extract and spec-fidelity is exposed to this size variability. The system has no
per-input-file size check before construction of the combined embed; it only checks the total
aggregate. A large spec file alone (117.9 KB) already consumes 92% of `MAX_ARG_STRLEN` before
`roadmap.md` (34.2 KB) is added.

**Evidence**:
- `inputs=[config.spec_file, merge_file]` at `executor.py:429`
- `spec-cross-framework-deep-analysis.md` = 30 KB → worked; `v2.25-spec-merged.md` = 117.9 KB → fails
- test-strategy, diff, debate steps all embed pipeline-generated outputs (bounded by prior step behavior)
- No per-file size check before `_embed_inputs()` is called

**Likelihood assessment**: To be determined by adversarial debate.

---

## Root Cause 3: The Embed Strategy Has No Awareness of Argument Length vs. Content Length

**Hypothesis**: The embed fallback mechanism was designed to handle content that is "too large
for the model's context" (hence the 200 KB limit as a rough proxy for token budgets), not to
handle OS-level argument length constraints. The two limits are conflated: `_EMBED_SIZE_LIMIT`
tries to serve both purposes (context window proxy AND OS argument guard) but was calibrated
for only one of them. The correct fix for OS limits is not a content size check at all — it is
architectural: prompts above a certain byte threshold should always be written to a temp file
and passed via stdin or `--file`, regardless of `_EMBED_SIZE_LIMIT`. The current fallback
switches to `--file` for the *inputs* but still passes the *prompt* (which contains the
embedded inputs) as a `-p` CLI argument, so the fallback does not actually solve the OS
constraint even when it triggers.

**Evidence**:
- `build_command()` in `process.py:69-87` always passes prompt via `-p self.prompt` as a CLI argument
- The fallback path at `executor.py:184-188` switches to `--file` for `step.inputs` but
  `effective_prompt = step.prompt` with no file embedding — the prompt itself is the large string
- Even if `_EMBED_SIZE_LIMIT` were lowered to 100 KB, the prompt template (~4 KB) +
  any non-trivial spec file would still hit `MAX_ARG_STRLEN`
- The fallback was designed as a context-window optimization, not an OS-constraint solution

**Likelihood assessment**: To be determined by adversarial debate.

---

## Next Steps

Three parallel adversarial debates will evaluate each root cause's likelihood of being
the **primary** root cause. Results will be reconciled to nominate the most actionable
true cause.

See:
- `arg-too-long-debate-rc1.md` — RC1 debate
- `arg-too-long-debate-rc2.md` — RC2 debate  
- `arg-too-long-debate-rc3.md` — RC3 debate
- `arg-too-long-reconciliation.md` — Final reconciliation and solution brainstorm
