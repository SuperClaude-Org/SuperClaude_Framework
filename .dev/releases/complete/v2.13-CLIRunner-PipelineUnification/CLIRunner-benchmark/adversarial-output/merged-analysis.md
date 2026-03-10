---
title: "Architectural Analysis: Inline Prompt Embedding vs --file for Roadmap Pipeline"
authors: [analysis-agent-alpha, analysis-agent-beta]
scope: src/superclaude/cli/{pipeline,sprint,roadmap}/
analysis_type: adversarial-merged-architectural-decision
base_variant: B (skeptical-counterargument)
merge_method: /sc:adversarial --depth deep
confidence: 0.82
---

<!-- Provenance: This document was produced by /sc:adversarial -->
<!-- Base: Variant B (analysis-agent-beta, skeptical-counterargument) -->
<!-- Merge date: 2026-03-05 -->

# Architectural Analysis: How Should the Roadmap Pipeline Pass File Content to Subprocesses?

## Executive Summary

The SuperClaude CLI's roadmap executor uses `--file` flags to pass input files to `claude -p` subprocesses, while the sprint executor uses inline `@file` references in the prompt string. The roadmap approach produces 0-byte output files when run from a bare terminal. This analysis examines whether switching to inline prompt embedding is the correct fix, through structured adversarial debate with ground-truth codebase verification.

**Key findings**:
1. The `--file` semantics claim (that the flag only accepts remote `file_id:relative_path` format) is **unverified** and must be checked before proceeding
2. Sprint's `@file` mechanism works **differently than initially claimed** — it relies on LLM tool-based file discovery, not content injection
3. The correct approach is **Python-side file reading + prompt embedding** — a third mechanism distinct from both existing approaches
4. One factual claim in the original proposal was **refuted by ground-truth evidence** (dead code assertion)

---

## 1. The Behavioral Split Is Real

<!-- Source: Base (original) + Variant A code evidence (Change #1) -->

The pipeline has two consumers using fundamentally different content-passing strategies:

### Sprint: Inline `@file` references

File: `src/superclaude/cli/sprint/process.py`, lines 47-54

```python
def build_prompt(self) -> str:
    phase_file = self.phase.file
    return (
        f"/sc:task-unified Execute all tasks in @{phase_file} "
        f"--compliance strict --strategy systematic\n"
        ...
    )
```

The `@{phase_file}` reference is embedded in the prompt string. The Claude process resolves it after launch.

### Roadmap: `--file` flags via `extra_args`

File: `src/superclaude/cli/roadmap/executor.py`, lines 103-117

```python
proc = ClaudeProcess(
    prompt=step.prompt,
    ...
    extra_args=[
        arg
        for input_path in step.inputs
        for arg in ("--file", str(input_path))
    ],
)
```

This appends `--file /absolute/path` to the subprocess argv. The base `ClaudeProcess.build_command()` in `pipeline/process.py:58-76` places these after `-p <prompt>`.

**Verified**: Both code paths confirmed in source. This divergence is the root of the investigation.

---

## 2. Is `--file` Actually Semantically Wrong?

<!-- Source: Base (original, modified) — expanded with ground-truth verification (Change #3) -->

### The claim under examination

The original proposal (Variant A, Section 2b) asserts:

> "The Claude CLI's `--file` flag expects `file_id:relative_path` format for remote file downloads — it is not a local filesystem path injector."

### Verification status

| Check | Status | Finding |
|-------|--------|---------|
| `claude --help` output for `--file` | **PENDING** | Not yet verified — must be checked before any refactoring |
| `.err` file from failed roadmap run | **PENDING** | Stderr should be examined for CLI error messages |
| Isolated test: `claude -p "test" --file /tmp/test.md` | **PENDING** | Would definitively resolve the semantics question |
| Alternative hypotheses for 0-byte output | **OPEN** | Timeout, prompt complexity, gate strictness all remain plausible |

### Critical assessment

This is the **load-bearing factual claim** of the entire analysis. If `--file` does accept local paths and the 0-byte output has another cause (timeout, prompt issues, gate logic), then the problem may be simpler to fix than a full architectural change. **No refactoring should proceed until this is empirically verified.**

### What IS confirmed

- The 0-byte output failure is reported as observed behavior (not disputed)
- Sprint using `@file` does NOT exhibit this failure (not disputed)
- The two mechanisms ARE different (confirmed by source code)
- `build_command()` uses `--print` mode (`pipeline/process.py:62`), which may affect how both `--file` and `@file` behave

---

## 3. Sprint's `@file` Is Not What It Appears

<!-- Source: Base (original, modified) — enhanced with code evidence (Change #1) -->

### The mechanism distinction

The original proposal claimed sprint's `@file` syntax is "resolved by the Claude process itself after launch" — implying content injection. However, closer analysis reveals:

1. **`@file` is a Claude Code convention**, not a Claude CLI convention. In `--print` mode (confirmed at `pipeline/process.py:62`), the `@` reference may be resolved differently than in interactive mode.

2. **Sprint likely works because the LLM agent actively reads files** via its `Read` tool during execution. The file content is NOT injected into the prompt at launch time — the LLM discovers it.

3. **Roadmap's files are generated pipeline intermediates** (extraction.md, roadmap-A.md, etc.). These are not pre-existing project files the LLM can naturally discover. The `@file` approach introduces nondeterminism — the LLM might fail to read the file, misinterpret the reference, or read different content if a concurrent step is writing.

### Implication

Adopting sprint's `@file` pattern for roadmap would trade one problem (`--file` semantics) for another (nondeterministic file access). The correct solution is a **third approach**: Python-side file reading + deterministic prompt embedding.

---

## 4. The `_build_subprocess_argv` Function Is NOT Dead Code

<!-- Source: Base (original, modified) — verified with ground-truth evidence (Change #3) -->

### The original claim (refuted)

Variant A (Section 3c) claimed: "`roadmap/executor.py:53-76` defines `_build_subprocess_argv()` which manually constructs a `claude` command list. This function is never called."

### Ground-truth evidence

The function IS called from **7+ test locations**:

| File | Lines | Usage |
|------|-------|-------|
| `tests/roadmap/test_executor.py` | 21, 171 | Imported and called in test |
| `tests/roadmap/test_cli_contract.py` | 10, 69, 91, 112, 129, 321, 327 | Imported and called in 6 test cases |

These tests validate the subprocess argument construction contract (context isolation, forbidden flags, model injection). The function is **test infrastructure**, not dead code.

### Architectural note

The function IS architecturally redundant with `ClaudeProcess.build_command()` — both construct `claude` CLI commands. However, `_build_subprocess_argv` exists to validate the CONTRACT of what subprocess args should look like, independent of the `ClaudeProcess` implementation. Deleting it requires refactoring the tests to validate `build_command()` output instead.

---

## 5. Sprint's Pipeline Bypass

<!-- Source: Base (original) + Variant A evidence (Change #1) -->

### Confirmed: Sprint does NOT use `execute_pipeline()`

Grep for `execute_pipeline` in `src/superclaude/cli/sprint/` returns **zero matches**. Sprint has a completely independent orchestration loop in `sprint/executor.py`.

Roadmap uses `execute_pipeline()` at `roadmap/executor.py:494`:
```python
results = execute_pipeline(
    steps=steps,
    config=config,
    run_step=roadmap_run_step,
    on_step_start=_print_step_start,
    on_step_complete=_print_step_complete,
)
```

### Assessment

Sprint's independent orchestration may be intentional — sprint has TUI monitoring, watchdog stall detection, and rich diagnostic collection that are tightly coupled to its execution loop. Whether this is "harmful duplication" or "appropriate separation" is a design judgment call, not a defect. The ~90 lines of process method overrides (`sprint/process.py:91-179`) add sprint-specific `debug_log()` calls that provide phase-specific diagnostic context.

---

## 6. Risks of Inline Embedding That Must Be Addressed

<!-- Source: Base (original) + Variant A mitigations (Change #5) -->

### 6.1 Prompt injection surface

**Risk**: Embedding pipeline-generated file content directly into the next step's prompt means any content becomes executable prompt instructions. A generated roadmap variant could contain "Ignore previous instructions..." patterns.

**Proposed mitigations** (from debate Round 2):
- Use `<file path="relative/path">content</file>` provenance tags that Claude recognizes as content boundaries
- Sanitize embedded content by escaping known prompt-significant patterns
- Consider whether `--file` provides any content sandboxing (must be verified)

**Status**: Mitigation design needed before implementation.

### 6.2 Encoding edge cases

**Risk**: Python-side file reading requires handling UTF-8, BOM, null bytes, binary content. The current `--file` approach delegates this to the CLI.

### 6.3 Prompt size monitoring

**Risk**: With inline embedding, prompts grow as pipeline steps accumulate inputs. The merge step takes 4 input files. The "2MB stdin fallback" mentioned in the original proposal was not designed — gate checking, logging, and prompt hashing behavior under stdin mode needs specification.

### 6.4 Testing burden

**Risk**: Prompt-building functions in `roadmap/prompts.py` become impure (must read files, handle I/O errors). Current functions are pure (path in, string out).

**Proposed mitigation** (from debate Round 2): Extract file reading into a single `load_inputs(step) -> dict[Path, str]` function. Prompt functions remain pure — they accept content strings, not paths. The `load_inputs` function is the single I/O boundary that tests mock.

---

## 7. Consensus Points from Adversarial Debate

<!-- Source: Variant A + Variant B debate consensus (Change #4) -->

After 3 rounds of structured adversarial debate (convergence: 84%), both advocates agreed on:

1. **The `--file` semantics claim must be verified** before any refactoring proceeds (empirical test required)
2. **The dead code claim was factually wrong** — `_build_subprocess_argv` has 7+ test callsites
3. **Inline embedding provides better debuggability** — a single-string prompt is objectively easier to log, hash, and replay
4. **The proposal should be reframed** as "Python-side reading + prompt embedding" — NOT "adopt sprint's pattern" (sprint's mechanism is LLM file discovery, not content injection)
5. **Prompt injection risk must be addressed** with content boundary markers in the implementation design

---

## 8. Recommended Implementation (Post-Verification)

<!-- Source: Variant A, Section 5 (reframed per Round 3 consensus) — Change #2 -->

**Prerequisite**: Complete verification items in Section 2 before proceeding.

If verification confirms that `--file` is unsuitable for local path injection (or that inline embedding is superior regardless):

1. **Create `load_inputs()` helper**: In the Python executor layer, read input files from `step.inputs` paths into a `dict[Path, str]`. This is the single I/O boundary.

2. **Embed content with provenance tags**: Format as `<file path="relative/path">content</file>` in the prompt string. This provides content boundaries for prompt injection mitigation.

3. **Remove `extra_args` `--file` usage**: In `roadmap_run_step()` (`roadmap/executor.py:112-116`), replace the `extra_args` list comprehension with inline embedding.

4. **Add size guard**: If combined prompt exceeds 2MB, pipe via subprocess stdin instead of argv. Design gate checking and logging behavior for the stdin path.

5. **Refactor `_build_subprocess_argv` tests**: Update `test_cli_contract.py` and `test_executor.py` to validate `ClaudeProcess.build_command()` output instead. Then consider whether the standalone function still serves a purpose.

---

## 9. Verification Checklist

<!-- Source: Base (original, modified) — enriched with debate-validated scoring (Change #6) -->

| # | Claim | Verification | Status | Priority |
|---|-------|-------------|--------|----------|
| 1 | `--file` is semantically wrong for local paths | `claude --help` output + isolated test + stderr from failed runs | **PENDING** | Critical |
| 2 | `@file` is portable in `--print` mode | Test `claude --print -p "read @/tmp/test.md"` behavior | **PENDING** | High |
| 3 | Sprint works via LLM file discovery (not injection) | Examine sprint subprocess stdout for Read tool calls | **PENDING** | High |
| 4 | `_build_subprocess_argv` is dead code | Full-repo grep including tests | **VERIFIED: FALSE** — 7+ test callsites | Resolved |
| 5 | Sprint duplication is harmful vs. intentional | Analyze callback complexity if sprint used execute_pipeline | **PENDING** | Low |
| 6 | Inline prompt injection risk is acceptable | Design mitigation with `<file>` boundary tags; test with adversarial content | **PENDING** | High |

**Decision gate**: Items 1, 2, and 6 must be resolved before implementation proceeds.

---

## Adversarial Process Metadata

- **Pipeline**: /sc:adversarial --compare variant-A,variant-B --depth deep --interactive
- **Base selected**: Variant B (score: 0.780) over Variant A (score: 0.700)
- **Margin**: 8.0%
- **Deciding factors**: Correctness (B: 5/5 vs A: 2/5), debate performance (B: 11 points vs A: 3)
- **Convergence**: 84% (threshold: 80%)
- **Rounds**: 3 (deep mode)
- **Full artifacts**: See `adversarial/` directory
