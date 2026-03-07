# Adversarial Debate: File Passing Strategy for Roadmap Pipeline

## Metadata

- **Date**: 2026-03-05
- **Subject**: `--file` flag vs. inline content embedding for `claude -p` subprocesses
- **Pipeline**: `superclaude roadmap run` (8-step adversarial pipeline)
- **Orchestrator**: Debate Orchestrator (neutral, process-only)

---

## Preamble: Factual Corrections

Before scoring any arguments, the orchestrator must correct a critical factual error that affects the entire debate.

**The `--file` flag does NOT do what Approach A advocates claim.**

Evidence from `claude --help` (checked 2026-03-05):

```
--file <specs...>  File resources to download at startup.
                   Format: file_id:relative_path (e.g., --file file_abc:doc.txt file_def:img.png)
```

The `--file` flag is a **remote file download mechanism** that accepts `file_id:relative_path` pairs. It does NOT accept local filesystem paths and inject them as context. The current roadmap executor at `src/superclaude/cli/roadmap/executor.py` line 68 passes `--file /absolute/path`, which is semantically incorrect usage of this flag.

**The sprint runner's `@` syntax also has constraints.** The sprint process builds prompts containing `@{phase_file}`, which is Claude Code's interactive `@`-mention syntax. In `-p` (print) mode, `@` references may or may not be resolved depending on whether the subprocess runs in a context where file resolution is available.

**Both approaches as currently implemented have correctness issues.** This reframes the debate from "which works" to "which can be made to work correctly."

The **actually viable mechanisms** for passing file content to `claude -p` subprocesses are:

1. **Inline in `-p` prompt**: Read file, embed content in the prompt string
2. **Stdin piping**: `echo "$prompt" | claude -p` or `cat files prompt | claude -p`
3. **System prompt file**: `--system-prompt` with file content
4. **Append system prompt**: `--append-system-prompt` with file content

---

## Round 1: Challenge Each Argument

### Argument A1: Shell Safety (Pro `--file`)

> "Inline requires escaping backticks, quotes, dollar signs in markdown content. `--file` bypasses shell interpolation entirely."

**Factual Accuracy**: PARTIALLY TRUE, but misdirected.

The claim about shell escaping is real. Markdown files containing backticks (`` ` ``), dollar signs (`$`), double quotes (`"`), and single quotes (`'`) will cause shell interpretation issues if naively interpolated into a `-p "..."` argument.

However, the current implementation (`ClaudeProcess.build_command()` at `pipeline/process.py:58-76`) builds a Python `list[str]` passed to `subprocess.Popen()`. **Python's subprocess module does NOT invoke a shell** when given a list. The prompt string is passed as a single argv element with zero shell interpolation. This completely neutralizes the shell safety concern.

The only scenario where shell escaping matters is if someone constructs the command as a shell string (e.g., `os.system(f'claude -p "{prompt}"')`), which this codebase does not do.

**Severity**: Theoretical (0/10 in current architecture)

**Mitigation**: Already mitigated by `subprocess.Popen(list)` -- no shell involved.

**Argument Strength**: **2/10** -- The concern is real in principle but fully neutralized by the existing implementation pattern. The claim survives only for hypothetical future callers that use shell strings.

---

### Argument A2: ARG_MAX Limits (Pro `--file`)

> "Later pipeline steps reference 3-4 accumulated artifacts (60-100KB combined). `--file` passes short paths with no size ceiling."

**Factual Accuracy**: PARTIALLY TRUE, but overstated.

System `ARG_MAX` on this machine is **3,200,000 bytes** (3.2MB). Linux kernels since 2.6.23 (2007) typically set this to 2MB+. The claim of "60-100KB combined" is well within the 3.2MB limit -- representing only 2-3% of capacity.

Looking at actual pipeline steps:
- **Step 6 (merge)**: Receives `score_file + roadmap_a + roadmap_b + debate_file` -- 4 files. If each is 200-400 lines of markdown, that is roughly 40-80KB total. Still under 3% of ARG_MAX.
- **Worst case**: Even if all artifacts grew 5x, the total would be ~400KB, or 12.5% of ARG_MAX.

Furthermore, `ARG_MAX` applies to the **total environment + argv** size, not just the prompt. But the environment is typically 10-50KB, leaving ample room.

**Severity**: Minor for current pipeline; Significant only if file sizes grow 10-30x beyond current estimates.

**Mitigation**: Monitor combined prompt size. If it ever approaches 1MB, switch to stdin piping (`Popen` with `stdin=PIPE` and `process.communicate(prompt_bytes)`), which has no size limit.

**Argument Strength**: **3/10** -- Theoretically valid, practically irrelevant for this pipeline's scale. The escape hatch (stdin piping) is trivial to implement.

---

### Argument A3: Token Budget Discipline (Pro `--file`)

> "CLI can present files as distinct labeled context blocks, giving the model clearer provenance for multi-file steps."

**Factual Accuracy**: SPECULATIVE.

This argument assumes that `--file` (if it worked as imagined) would present files to the model with distinct labels/provenance. There is no evidence this is how the Claude CLI formats file context internally. It may simply concatenate file contents into the context window.

With inline embedding, the orchestrator has **complete control** over provenance labeling:

```
## File: roadmap-opus.md
<content here>

## File: roadmap-haiku.md
<content here>
```

This explicit labeling may actually provide **better** provenance than whatever implicit formatting `--file` would use, because the prompt author controls the framing.

**Severity**: Theoretical

**Mitigation**: Inline embedding with explicit section headers provides equivalent or better provenance control.

**Argument Strength**: **3/10** -- Reasonable intuition, but the inline approach can match or exceed this benefit with explicit formatting.

---

### Argument B1: Portability (Pro Inline)

> "`--file` requires session token, breaking bare terminals, CI, Docker, cron, SSH. Inline works everywhere."

**Factual Accuracy**: TRUE, and actually understated.

The `--file` flag as documented requires `file_id:relative_path` format, which implies server-side file resolution. This is even more restrictive than the original claim -- it is not just about session tokens, but about the flag's entire semantic model being incompatible with local file passing.

Inline embedding via `subprocess.Popen` with the prompt as an argv element works in every environment:
- Bare terminal (verified: sprint runner pattern)
- CI/CD pipelines
- Docker containers
- Cron jobs
- SSH sessions
- Any environment where `claude` binary is in `PATH`

The sprint runner's operational track record confirms this. It has been running successfully in the same codebase using prompt strings passed to `-p`.

**Severity**: Critical -- This is a hard blocker for Approach A as currently conceived.

**Mitigation for A**: None available. The `--file` flag does not support local file paths. The approach would need to be redesigned around a different mechanism entirely (e.g., stdin piping), at which point it is no longer "Approach A" as described.

**Argument Strength**: **9/10** -- This is the decisive argument. Approach A as described is not implementable with the current CLI.

---

### Argument B2: Debuggability (Pro Inline)

> "Inline gives you the exact prompt as a single loggable, hashable, replayable string. With `--file`, the fully-assembled input is invisible to your code."

**Factual Accuracy**: TRUE.

With inline embedding, the orchestrator sees the complete prompt that will be sent. This enables:
- **Logging**: Write the exact prompt to the execution log for post-mortem analysis
- **Hashing**: Deterministic content hashing for cache invalidation and replay detection
- **Replay**: Copy-paste the prompt to reproduce any step manually
- **Diffing**: Compare prompts across runs to debug behavioral changes

With any external-file approach, the orchestrator knows what files it *requested* but not how the subprocess *assembled* them into its context. If the subprocess fails, diagnosing whether the issue was prompt construction vs. model behavior requires reconstructing the full context manually.

The roadmap pipeline already saves `.roadmap-state.json` with per-step metadata. Inline prompts integrate naturally with this existing audit trail.

**Severity**: Significant for operational maintenance.

**Mitigation for A**: Could log the intended prompt + file list, but this is a reconstruction, not the actual input.

**Argument Strength**: **7/10** -- Genuine operational advantage with clear maintenance benefits.

---

### Argument B3: Atomic Error Handling (Pro Inline)

> "Inline fails early (before subprocess spawn) if a file is missing. `--file` creates a split failure domain."

**Factual Accuracy**: TRUE.

With inline, the orchestrator reads files in Python before building the prompt:

```python
content = path.read_text()  # FileNotFoundError here = clear, immediate
prompt = f"...\n{content}\n..."
proc = ClaudeProcess(prompt=prompt, ...)
```

If a file is missing, the error occurs in the orchestrator's process with a clear stack trace, before any subprocess is spawned. The error is synchronous, catchable, and attributable.

With `--file` (or any external reference), the subprocess must resolve files after launch. Failures occur in the child process, reported via exit codes and stderr. The orchestrator must parse error output to determine *which* file failed and *why*. For parallel step groups (like generate-a + generate-b), this creates additional complexity in error attribution.

**Severity**: Significant -- Reduces failure diagnosis from "parse child stderr" to "catch Python exception."

**Mitigation for A**: The child process's stderr is already captured to `.err` files, so failures are eventually discoverable. But the failure domain remains split.

**Argument Strength**: **6/10** -- Real advantage, though the existing `.err` file capture partially mitigates it.

---

## Round 1 Score Summary

| Argument | Claimed For | Factual? | Severity | Mitigated? | Strength |
|----------|------------|----------|----------|------------|----------|
| A1: Shell safety | `--file` | Partially | Theoretical | Yes (Popen list) | 2/10 |
| A2: ARG_MAX | `--file` | Partially | Minor | Yes (stdin fallback) | 3/10 |
| A3: Token provenance | `--file` | Speculative | Theoretical | Yes (inline headers) | 3/10 |
| B1: Portability | Inline | True+ | Critical | No mitigation for A | 9/10 |
| B2: Debuggability | Inline | True | Significant | Partial for A | 7/10 |
| B3: Atomic errors | Inline | True | Significant | Partial for A | 6/10 |

**Round 1 Approach A total**: 8/30
**Round 1 Approach B total**: 22/30

---

## Round 2: Cross-Cutting Analysis

### 2.1 Hybrid Approaches

**Option H1: Inline by default, stdin for large payloads**

The most practical hybrid:
- For steps with small inputs (extract, test-strategy): embed file content directly in the `-p` prompt string
- For steps approaching ARG_MAX concerns (merge with 4 files): pipe the prompt via stdin to `Popen(stdin=PIPE)` using `process.communicate(prompt.encode())`

This preserves all inline benefits (debuggability, atomicity, portability) while removing the ARG_MAX ceiling entirely. The `ClaudeProcess` class already uses `Popen`; switching from argv to stdin is a minor change.

**Option H2: Structured prompt with inline content + metadata headers**

Build prompts with explicit file provenance:

```
<file path="roadmap-opus.md" lines="247" sha256="abc123">
... content ...
</file>

<file path="roadmap-haiku.md" lines="312" sha256="def456">
... content ...
</file>

<instructions>
Compare the two roadmap variants above...
</instructions>
```

This gives the model clear file boundaries while keeping everything inline. The sha256 hashes enable cache validation.

**Option H3: Temporary file with assembled prompt, passed via stdin**

Write the complete assembled prompt to a temp file, then `cat tempfile | claude -p`. This gives:
- Full debuggability (the temp file IS the exact input)
- No ARG_MAX constraint (stdin has no limit)
- Portability (works everywhere)
- Easy replay (`cat tempfile | claude -p` from command line)

**Recommended hybrid**: H1 (inline default) with H2's metadata headers. This is the simplest change from current architecture, requires no temp files, and handles all current pipeline sizes.

### 2.2 Sprint Runner's Track Record

The sprint runner at `src/superclaude/cli/sprint/process.py` demonstrates:

1. **Prompt-string approach works**: It builds prompts as Python strings and passes them via `Popen` without shell involvement
2. **`@` syntax in `-p` mode**: The sprint uses `@{phase_file}` in prompts, which relies on Claude Code's `@`-mention resolution. This works when spawned from within a Claude Code session but may not work from bare terminals. This is a **latent portability bug** in the sprint runner too.
3. **No `--file` usage**: The sprint runner does not use `--file` at all, suggesting its developers already concluded that inline/prompt-based approaches are more reliable.

The sprint runner's success validates the inline pattern, with the caveat that its `@` references may have the same bare-terminal portability concern that the roadmap's `--file` has.

### 2.3 Operational Constraints

Hard constraints for this decision:

1. **Must work from bare terminals TODAY** -- The roadmap CLI is broken in bare terminals right now. The fix must restore bare-terminal operation. This eliminates any approach requiring session tokens or Claude Code session context.

2. **Pipeline produces markdown artifacts** -- Files contain backticks, code blocks, YAML frontmatter. Shell escaping would be a concern IF shell invocation were used, but `subprocess.Popen(list)` eliminates this.

3. **Files are generated sequentially** -- Each step's output feeds later steps. The orchestrator already reads files for gate checking (`gate_passed` reads output files). Adding a `read_text()` call for prompt assembly is zero additional I/O since the OS will serve from page cache.

4. **8 steps, max 4 inputs per step** -- This is a fixed, small pipeline. There is no dynamic scaling concern.

### 2.4 Maintenance Burden

**Inline approach maintenance**:
- Prompt builders (`prompts.py`) remain pure functions returning strings
- File reading happens in the executor, adding ~3 lines per step
- No dependency on CLI flag semantics that may change between Claude versions
- No need to track `--file` flag behavior across CLI updates
- Debugging requires only: "print the prompt string"

**`--file` approach maintenance** (hypothetical, if a working local-file flag existed):
- Depends on external CLI flag contract remaining stable
- Must track CLI version compatibility
- File resolution errors are opaque (child process stderr)
- Testing requires either mocking the CLI or integration tests with the real binary
- Every CLI update requires verifying `--file` still works as expected

**Verdict**: Inline has strictly lower maintenance burden because it depends only on `subprocess.Popen` (Python stdlib, stable for 20+ years) and `claude -p` accepting a prompt string (the most basic CLI contract).

---

## Final Verdict: Weighted Scoring

### Scoring Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Portability | 3x | Works in bare terminals, CI, Docker, cron, SSH |
| Correctness | 2x | Actually implementable and produces correct results |
| Debuggability | 2x | Loggable, replayable, diagnosable failures |
| Scalability | 1x | Handles growth in file count/size |
| Architectural Cleanliness | 1x | Simplicity, maintainability, minimal dependencies |

### Approach A: `--file` Flag

| Criterion | Score (1-10) | Weighted | Rationale |
|-----------|-------------|----------|-----------|
| Portability | 1 | 3 | Flag does not support local files; fundamentally broken for this use case |
| Correctness | 1 | 2 | Current `--file path` usage is semantically incorrect per CLI docs |
| Debuggability | 4 | 8 | File list is loggable, but assembled context is not visible |
| Scalability | 7 | 7 | Path-based references scale well (if they worked) |
| Arch Cleanliness | 5 | 5 | Clean separation of concerns, but external dependency risk |
| **Total** | | **25/90** | |

### Approach B: Inline Content Embedding

| Criterion | Score (1-10) | Weighted | Rationale |
|-----------|-------------|----------|-----------|
| Portability | 10 | 30 | Works everywhere `claude -p` works; proven by sprint runner |
| Correctness | 9 | 18 | Reads files in Python, embeds in prompt; only risk is ARG_MAX at extreme scale |
| Debuggability | 9 | 18 | Complete prompt is a single inspectable string |
| Scalability | 6 | 6 | ARG_MAX at 3.2MB is sufficient; stdin fallback removes ceiling |
| Arch Cleanliness | 8 | 8 | Minimal dependencies; pure Python + Popen |
| **Total** | | **80/90** | |

### Winner

**Approach B: Inline Content Embedding wins decisively at 80/90 vs 25/90.**

**Confidence Level: HIGH (95%)**

The debate is not close. Approach A is built on a misunderstanding of the `--file` flag's purpose. Even if a hypothetical local-file flag existed, Approach B would still win on debuggability and atomic error handling. The portability advantage alone (weight 3x, score 10 vs 1) makes this a 30-point gap on a single criterion.

### Recommended Implementation

1. **Modify `prompts.py`** prompt builders to accept file *content* (not paths) as parameters, or add a thin wrapper that reads files before calling existing builders.

2. **Modify `executor.py`** `_build_steps()` to read input files and inject content into prompts. Remove `--file` from `extra_args`.

3. **Add provenance headers** using the H2 pattern:
   ```
   <file path="extraction.md">
   ... content ...
   </file>
   ```

4. **Add size guard**: If combined prompt exceeds 2MB, switch to stdin piping via `Popen(stdin=PIPE)` + `process.communicate()`.

5. **Keep `step.inputs` metadata** for logging and gate-checking, even though content is inlined.

---

## Appendix: Evidence Sources

| Evidence | Location | Finding |
|----------|----------|---------|
| `--file` flag docs | `claude --help` | Expects `file_id:relative_path`, not local paths |
| ARG_MAX | `getconf ARG_MAX` | 3,200,000 bytes on this system |
| Roadmap executor | `src/superclaude/cli/roadmap/executor.py:68` | Uses `--file str(input_path)` (incorrect usage) |
| Pipeline process | `src/superclaude/cli/pipeline/process.py:58-76` | Uses `Popen(list)` -- no shell involved |
| Sprint process | `src/superclaude/cli/sprint/process.py:47-80` | Uses inline prompt with `@` syntax, no `--file` |
| Prompt builders | `src/superclaude/cli/roadmap/prompts.py` | Pure functions returning strings, accept Path objects but don't read them |
