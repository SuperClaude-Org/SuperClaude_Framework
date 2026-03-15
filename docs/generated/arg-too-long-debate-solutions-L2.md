# Adversarial Debate: Level 2 Solutions (2A + 2B)

**Subject**: Per-file size guard (2A) and spec file warning (2B) as additions to Level 1 fixes
**Date**: 2026-03-15
**Format**: 2-round adversarial debate

---

## Established Context

- **RC1 fix (1A+1B)**: Derive `_EMBED_SIZE_LIMIT` from `MAX_ARG_STRLEN` and guard full composed string. Consensus primary fix.
- **Current `_EMBED_SIZE_LIMIT`**: 200 KB (broken). Proposed (1A): ~120 KB.
- **Current `_embed_inputs()`**: Reads all files into memory before any size check (line 57-70 in executor.py).
- **Spec file**: 117.9 KB. Pipeline artifacts: extraction (35.3 KB), roadmap (34.2 KB), debate (20 KB), diff (11.3 KB).
- **Spec-fidelity step**: embeds spec (117.9 KB) + extraction (35.3 KB) + roadmap (34.2 KB) = 187.4 KB combined.
- **Extract step**: embeds spec file as sole input (117.9 KB).
- **The guard at line 175**: `if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT` -- this runs *after* `_embed_inputs()` has already read all files.

---

## Round 1

### ADVOCATE (2A+2B add meaningful value beyond 1A+1B)

**Claim 1: 2A prevents unnecessary I/O that 1A+1B cannot.**

The current code flow is: `_embed_inputs()` reads *every* input file into memory (line 68: `Path(p).read_text()`), concatenates them, then the guard at line 175 checks the total size. With 1A+1B applied, a 117.9 KB spec file still gets read, concatenated with a 35.3 KB extraction and a 34.2 KB roadmap, producing a ~187 KB string -- only to have the guard reject it and fall back to `--file` flags.

Solution 2A's `_should_embed_inputs()` uses `.stat().st_size` (a metadata call, not a file read) to pre-screen files. The 117.9 KB spec file exceeds the 64 KB per-file limit, so the function returns `False` immediately. No files are read. No 187 KB string is constructed. This is not just defense-in-depth -- it is an efficiency improvement. On a pipeline with 9 steps where several steps take the spec as input, avoiding unnecessary reads of a 118 KB file is measurable.

**Claim 2: 2A catches a class of failure that 1A+1B's total-size guard misses.**

Consider a step that embeds a single 115 KB file with a 4 KB prompt. Total: 119 KB. With 1A+1B's ~120 KB limit, this passes the guard and gets embedded into the `-p` argument. But the 115 KB file alone is 90% of `MAX_ARG_STRLEN`. Any future prompt template growth (a few KB of additional instructions) would push it over the edge. The per-file guard at 64 KB would reject this immediately, providing a wider safety margin for individual files that are structurally too large to embed regardless of what else is in the pipeline.

**Claim 3: 2B provides operator-visible diagnostics at zero risk.**

Solution 2B is a pure `_log.warning()` call with no code path change. It fires at pipeline entry, before any steps execute. For a multi-step pipeline that may run for 30+ minutes, knowing at second zero that the spec file is large enough to trigger `--file` fallbacks is operationally useful. It costs nothing: no branching logic, no behavioral change, and the threshold constant (80 KB) does not interact with any guard. If it fires for a spec that does not actually cause problems, the message is informative -- it says "may trigger embed fallback," not "will fail."

**Claim 4: The per-file limit of 64 KB does not cause false positives for pipeline artifacts.**

The largest pipeline artifact is extraction at 35.3 KB. Roadmap is 34.2 KB. Debate is 20 KB. Diff is 11.3 KB. None of these exceed 64 KB. The only file that exceeds 64 KB is the user-supplied spec, which is exactly the file that *should* be routed to `--file` mode because it is the unbounded input. The 64 KB threshold is not conservative in practice -- it correctly separates pipeline-internal artifacts (bounded, generated) from user-supplied documents (unbounded, variable).

---

### CRITIC (2A+2B add complexity without sufficient benefit)

**Rebuttal to Claim 1: The I/O cost is negligible and the optimization is premature.**

Reading a 118 KB file takes approximately 0.1 ms on any modern filesystem with warm cache. Each pipeline step spawns a `claude` subprocess that runs for minutes. The "unnecessary I/O" of reading one file that gets rejected by the guard is noise against a pipeline that runs for 30+ minutes total. Introducing a second function (`_should_embed_inputs()`) with its own constant (`_PER_FILE_EMBED_LIMIT`) to save 0.1 ms is textbook premature optimization. The real cost is cognitive: future maintainers now need to understand two guard functions, two constants, and their interaction.

**Rebuttal to Claim 2: The 115 KB edge case is already handled by 1A+1B.**

The Advocate constructs a scenario where a 115 KB file + 4 KB prompt passes a 120 KB total guard. But 1B specifically measures the *full composed string* -- `step.prompt + "\n\n" + embedded`. For a 115 KB file, `_embed_inputs()` would produce approximately `len("# /path/to/file\n```\n") + 115 KB + len("\n```")` = ~115.03 KB. Adding the 4 KB prompt: ~119 KB. This is below 120 KB, so it passes. But here is the key: **it should pass**. The combined argument is 119 KB, which is below `MAX_ARG_STRLEN` (128 KB), so it will not crash. The 1A+1B guard already provides the safety margin (8 KB of `_PROMPT_TEMPLATE_OVERHEAD`). Adding a per-file guard that rejects a 115 KB file that would actually embed safely is a false positive -- it forces unnecessary `--file` fallback, which changes how Claude receives the content (as a resource attachment vs. inline prompt context), potentially degrading step quality.

**Rebuttal to Claim 3: Advisory warnings without remediation paths are noise.**

The 2B warning says "consider condensing if pipeline steps fail." This is not actionable for an automated pipeline. If a human is watching logs, they already know the spec file size. If they are not watching, the warning is lost in the log stream. More importantly, the warning fires at 80 KB but the actual danger zone (with 1A+1B applied) starts at around 112 KB (120 KB limit minus 8 KB overhead). A warning at 80 KB fires for spec files that are 28 KB below the problematic range -- pure noise.

**Rebuttal to Claim 4: The 64 KB constant is arbitrary and creates maintenance burden.**

The Advocate argues 64 KB correctly separates user files from pipeline artifacts. But this is coincidental today. If a future pipeline step produces a 70 KB artifact (a detailed test strategy, a comprehensive roadmap for a large project), the per-file guard would reject it even though the total embed (70 KB artifact + 4 KB prompt = 74 KB) is well within the 120 KB limit. Now you have three constants to tune: `_MAX_ARG_STRLEN`, `_EMBED_SIZE_LIMIT`, and `_PER_FILE_EMBED_LIMIT`. The interaction between them is non-obvious. The simpler design -- one total limit derived from the OS constraint -- is easier to reason about and harder to misconfigure.

**Core argument: 1A+1B is sufficient and correct. 2A+2B are premature layering.**

With 1A+1B applied, the guard measures the actual string that becomes the `-p` argument, and the limit is derived from the OS constraint. Any combination of files that exceeds the limit triggers fallback. Any combination below the limit succeeds. This is a complete and correct guard. Adding per-file checks is a second opinion that can disagree with the primary guard, creating confusion about which limit is "real."

---

## Round 2

### ADVOCATE (Responding to Critic)

**On premature optimization**: The Critic frames 2A as an I/O optimization and dismisses it. But the primary value of 2A is not performance -- it is **avoiding the read-then-discard pattern** that makes the code harder to reason about. Today, `_embed_inputs()` reads files without any size awareness. It is a pure reader function. The size check happens at the call site (line 175). This separation of concerns is fragile: the reader has no idea whether its output will be used or discarded. Solution 2A introduces a proper pre-check that makes the decision *before* committing to the read. This is a software engineering improvement, not a performance hack.

**On the 115 KB edge case**: The Critic argues that a 119 KB combined embed is "safe" because it is below `MAX_ARG_STRLEN`. But the Critic ignores that `MAX_ARG_STRLEN` (128 KB) applies to a single argument string, and the 1A overhead constant (8 KB) is an *estimate*. The actual overhead includes the prompt template, the `\n\n` separator, and the fenced block wrappers (`# path\n```\n...\n````) that `_embed_inputs()` adds. For a 115 KB file, the fenced block wrapper adds ~30 bytes -- trivial. But for multiple files, the overhead compounds. The per-file guard provides a structural guarantee that no single file dominates the embed budget, leaving room for the overhead to be estimated imprecisely.

More fundamentally, embedding a 115 KB file inline means the Claude subprocess receives a 119 KB `-p` argument. This is not just an OS risk -- it is a usability concern. The `--file` path may produce different (and potentially better) results for very large inputs because Claude treats resource attachments differently from inline prompt text. The per-file guard at 64 KB encodes a design preference: files larger than 64 KB are too large to be "inline context" and should be treated as resources.

**On the 80 KB warning threshold**: The Critic is right that 80 KB is below the danger zone. But the warning is not about preventing crashes -- it is about *setting expectations*. An operator who sees "spec file is 118 KB -- may trigger embed fallback" understands that some steps will use `--file` mode instead of inline embedding. If step outputs differ from expected patterns (because Claude processes file resources differently), the warning provides the first breadcrumb. This is standard observability practice. The cost of the warning is one `_log.warning()` call and one constant. If that is "noise," then most production logging is noise.

**On the 70 KB artifact scenario**: The Critic constructs a future where a pipeline artifact grows to 70 KB and the per-file guard causes a false positive. This is speculative. Today, the largest artifact is 35.3 KB. Pipeline artifacts are LLM-generated within token budgets and tend to be stable in size range. If a 70 KB artifact appears, the per-file limit should be reviewed -- that is what the constant is for. The alternative (no per-file guard) means the first sign of trouble is a crash or unexpected fallback, not a clear rejection with a log message.

**Concession**: The Critic is right that three constants is worse than one. I propose a refinement: derive `_PER_FILE_EMBED_LIMIT` from `_EMBED_SIZE_LIMIT` rather than hardcoding it independently:

```python
_PER_FILE_EMBED_LIMIT = _EMBED_SIZE_LIMIT // 2  # No single file > 50% of total budget
```

This reduces the constant count and makes the relationship explicit. With `_EMBED_SIZE_LIMIT = 120 KB`, the per-file limit becomes 60 KB -- close to the proposed 64 KB and still correctly rejecting the 117.9 KB spec file.

---

### CRITIC (Final rebuttal)

**On the read-then-discard pattern**: The Advocate reframes 2A as a software engineering improvement. But the proposed `_should_embed_inputs()` introduces a TOCTOU (time-of-check/time-of-use) issue that the Advocate has not addressed. The function calls `.stat().st_size` to get file sizes, then returns `True` or `False`. Later, `_embed_inputs()` calls `.read_text()` to get the actual content. Between these two operations, the file could be modified -- a concurrent pipeline step could write a larger output, or the filesystem could report a different size for non-ASCII content (`.stat().st_size` returns on-disk bytes; `.read_text()` + `.encode("utf-8")` returns decoded-then-re-encoded bytes; these differ for files with BOM markers, multi-byte sequences, or filesystem-level compression).

Is this TOCTOU race likely? No. Pipeline outputs are written before subsequent steps read them. But the Advocate claims 2A is a software engineering improvement -- and introducing a stat-then-read pattern where the stat result may not match the read result is not an engineering improvement. It is a new failure mode.

**On the derived constant**: The Advocate's refinement (`_PER_FILE_EMBED_LIMIT = _EMBED_SIZE_LIMIT // 2`) is better than independent constants. But it introduces a policy decision -- "no single file may exceed 50% of the total budget" -- that is not motivated by the OS constraint (which only cares about the total argument size). Why 50%? Why not 75%? This is an arbitrary ratio that will invite future debate. The simpler approach: rely on the total-size guard, which is directly tied to the OS constraint and requires no policy decisions about individual file proportions.

**On 2B**: I concede 2B is harmless. A `_log.warning()` with no behavioral effect is genuinely zero-risk. But "harmless" is not "valuable." The warning will be accurate (the spec is large) and unhelpful (the operator cannot change the spec size mid-pipeline, and the pipeline handles it correctly via `--file` fallback). If the pipeline handles large specs correctly (which 1A+1B ensures), the warning is telling the operator about a non-problem. This is the definition of noise.

**On the real problem with 2A**: The deeper issue is that 2A solves a problem that does not exist after 1A+1B. The current crash happens because `_EMBED_SIZE_LIMIT` is set above `MAX_ARG_STRLEN`. Once 1A+1B corrects this, the 117.9 KB spec file will be rejected by the total-size guard because `117.9 KB + 4 KB prompt > 120 KB limit`. The per-file guard is redundant for this case. For the extract step (spec as sole input), `117.9 KB + 4 KB > 120 KB` -- again rejected by the total-size guard. The per-file guard adds value only when a single file is large enough to be individually dangerous but the total is not -- and with a correctly calibrated total limit, that scenario results in a safe embed, not a crash.

**Final position**: 1A+1B is the complete fix. 2A adds a second guard that is redundant for the actual failure case, introduces a TOCTOU pattern, and adds a policy decision (per-file ratio) unrelated to the OS constraint. 2B is harmless but also unhelpful. If the team wants defense-in-depth, invest the effort in Level 3 (stdin delivery) which eliminates the entire class of failure rather than adding more proxy guards.

---

## Verdict

### Scoring

| Criterion | 2A (per-file guard) | 2B (startup warning) |
|-----------|---------------------|---------------------|
| Prevents crashes beyond what 1A+1B covers | Low -- 1A+1B's total-size guard handles all cases that would crash | N/A -- advisory only |
| Engineering value (code clarity) | Moderate -- pre-check before read is cleaner than read-then-discard | Low -- one log line |
| Risk of harm | Low -- false positives possible but unlikely given current artifact sizes | None -- no behavioral change |
| Maintenance cost | Moderate -- additional constant, function, tests, TOCTOU consideration | Low -- one constant, one log call |
| Redundancy with 1A+1B | High for the current failure case; moderate for future edge cases | N/A |

### Confidence: **58 / 100** (in favor of adopting 2A+2B)

The debate reveals that 2A+2B are genuinely defense-in-depth measures, but their incremental value over a correctly calibrated 1A+1B is modest. The Advocate's strongest arguments are structural (pre-check before read is better engineering) and forward-looking (per-file awareness catches future single-file growth). The Critic's strongest arguments are that the total-size guard is sufficient for correctness and that the per-file guard introduces complexity (TOCTOU, policy decisions) without preventing any crash that 1A+1B does not already prevent.

### Recommendations

1. **Adopt 2A with the derived-constant refinement, not the hardcoded 64 KB.** Use `_PER_FILE_EMBED_LIMIT = _EMBED_SIZE_LIMIT // 2` to maintain a single source of truth. This addresses the Critic's concern about arbitrary constants while preserving the Advocate's pre-check pattern.

2. **Adopt 2B but raise the threshold to match the embed limit.** Set `_SPEC_FILE_WARN_THRESHOLD = _EMBED_SIZE_LIMIT` (not 80 KB). This way the warning fires only when the spec file is large enough to actually trigger `--file` fallback, eliminating the noise concern.

3. **Address the TOCTOU concern explicitly.** In `_should_embed_inputs()`, document that `.stat().st_size` is an approximation and the total-size guard in `roadmap_run_step()` remains the authoritative check. The pre-check is an optimization, not the safety gate.

4. **Prioritize Level 3 over perfecting Level 2.** If engineering time is constrained, skip 2A+2B and invest in 3A (stdin delivery). Level 3 eliminates the entire class of failure; Level 2 adds proxy guards around a class that still exists.

5. **Defer 2A if 1A+1B is shipping immediately.** The per-file guard is a Phase 2 enhancement. Do not delay the 1A+1B fix to bundle 2A. Ship 1A+1B, unblock the pipeline, then evaluate whether 2A is worth the additional complexity.

### Summary

2A is a reasonable but non-essential improvement. 2B is harmless but should be tuned to avoid false warnings. Neither is required for correctness -- 1A+1B is the complete fix for the current crash. The moderate confidence score (58) reflects genuine ambiguity: the Advocate's case for defense-in-depth is principled, but the Critic's case for simplicity and investing in Level 3 instead is equally principled.
