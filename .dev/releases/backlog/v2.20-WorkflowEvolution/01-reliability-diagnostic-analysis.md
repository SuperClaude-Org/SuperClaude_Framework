# 01 — Reliability Spec + Sprint Diagnostic Framework Analysis

**Scope**: v2.19 Roadmap Pipeline Reliability spec + v2.03 Sprint Diagnostic Framework spec
**Focus**: Quality — internal contradictions, unstated assumptions, confidence gaps
**Date**: 2026-03-08
**Purpose**: Diagnostic only — no fixes proposed

---

## Part 1: Reliability Spec Analysis (v2.19)

### Internal Contradictions & Unstated Assumptions

**Contradiction 1: The spec assumes the bug is novel, but the architecture made it inevitable.**

The spec frames the `_check_frontmatter()` byte-position assertion as a bug to be fixed (RC-1, weight 40%). But the merged spec (v2.08) explicitly designed `gate_passed()` as "pure Python — it never invokes Claude to evaluate Claude's output." This design principle focused entirely on preventing *semantic* self-validation but never considered that *structural* validation might need tolerance for LLM output format variability. The byte-position check wasn't a mistake — it was the obvious implementation of "check if frontmatter exists." The unstated assumption was: Claude will produce clean output starting with `---`.

> Evidence: v2.19 spec §1.1: "Both retry attempts produce the same failure." — retries don't help because the output format variability is a property of the LLM, not a transient error.

**Contradiction 2: Confidence in the pipeline's end-to-end success rate is asserted without evidence.**

The spec calculates a 43% end-to-end success rate (`0.9⁸ ≈ 43%`) given a 10% preamble probability. This is presented as a diagnosis of the *current* state. But there is no empirical evidence for the 10% preamble rate — it's described as "conservatively estimated." The actual failure rate could be higher (Claude produces preamble more often with complex prompts) or lower (with prompt hardening). The confidence in the number undermines credibility without actually providing actionable data.

**Contradiction 3: RC-0 (`--verbose`) is listed as "uninvestigated" but receives a workstream.**

WS-0 allocates 30 minutes to investigate whether `--verbose` causes stdout pollution. This is the lowest-effort investigation in the spec. Yet the pipeline was presumably tested during development without anyone checking this basic configuration question. The existence of RC-0 as "uninvestigated" reveals that the development process completed an entire pipeline implementation without empirically testing the subprocess output it was built to parse.

> Evidence: v2.19 spec §1.3: "It is unknown whether `--verbose` with `output_format='text'` injects diagnostic text into stdout."

### Vague Requirements That Pass Review But Fail in Implementation

**FR-051.01**: Specifies the regex must "locate frontmatter using a pattern that matches `---` at a line start (not file start)." This is clear enough. But FR-051.02 says the match "MUST require at least one line containing a colon-separated key-value pair between the delimiters." The reference implementation uses `r'^---[ \t]*\n((?:[ \t]*\w[\w\s_-]*:.*\n)+)---[ \t]*$'`. This regex silently fails on frontmatter with blank lines between fields, or fields with multi-line YAML values (arrays, nested blocks). The spec says "key: value lines" but YAML frontmatter legitimately contains more than simple key-value pairs.

**Risk Register Optimism**: All risks are rated Low or Medium probability. "Regex matches horizontal rule as frontmatter" is rated Low probability — yet this is a well-known failure mode of regex-based YAML detection. "LLM fails to produce 10 frontmatter fields reliably" is rated Medium — but the entire spec exists because the LLM already failed to produce output in the expected format for *3* fields.

### Schema Drift: The Deeper Issue the Spec Partially Addresses

The spec identifies that the CLI port's extract prompt requests only 3 frontmatter fields while the source protocol specifies 17+. WS-4 addresses this. But the spec doesn't examine *why* schema drift occurred in the first place. The CLI pipeline was developed from the merged spec (v2.08), which defined the gate criteria inline. When the source protocol evolved (richer schemas), nobody propagated the changes to the CLI gates. There is no mechanism in the workflow to detect schema drift between the source protocol and the CLI implementation.

---

## Part 2: Sprint Diagnostic Framework Analysis (v2.03)

### Diagnostic Capabilities: Specified vs Built

The v2.03 spec defines a comprehensive diagnostic framework:

| Specified | Evidence of Build |
|-----------|-------------------|
| `--debug` flag with `debug.log` file | Referenced in v2.07 retrospective — log exists but with telemetry inaccuracies |
| Watchdog mechanism (`--stall-timeout`, `--stall-action`) | Specified in v2.03, listed as untested subsystem in v2.13 |
| Diagnostic test levels L0-L3 | L0 test harness described with fake claude scripts — unclear if fully implemented |
| Negative tests (6 failure modes) | Specified — but v2.13 identifies 6 "untested subsystems" including stall detection |
| `DiagnosticBundle`, `FailureClassifier`, `ReportGenerator` | Full class hierarchy specified — implementation status uncertain |

The v2.03 spec is extraordinarily detailed (1,526 lines), specifying exact log formats, shell scripts, pytest fixtures, and class hierarchies. But the v2.07 retrospective (first real sprint run) found 7 telemetry bugs, suggesting the diagnostic framework was either not fully implemented or not tested against real output.

### Ambiguous Spec Language Allowing Misinterpretation

**R2.1**: "Phase task is a shell script (not claude) that writes a properly formatted result file." This is clear for L0, but "properly formatted" is defined later in the spec. An implementer might write a result file that passes the *shell script's* format but not the *executor's* parser, because the executor's parsing logic is separately specified.

**R1.16**: "When `--debug` is active AND `stall_seconds > stall_timeout` AND `stall_timeout > 0`: execute stall action." The condition chain is clear, but "execute stall action" is vague — does the watchdog kill the subprocess? Kill the entire process group? The spec says `--stall-action kill` means "log + terminate process," but "terminate process" could mean SIGTERM, SIGKILL, or the SIGTERM→SIGKILL escalation defined elsewhere.

### "Assumed Working" Components Never Independently Validated

**The monitor→executor bridge**: The spec identifies that "the output monitor detects 'STALLED' status but the executor never acts on it" as the *root cause* of the original problem. The fix is a watchdog mechanism. But the watchdog depends on the monitor's `stall_seconds` field being accurate. If the monitor miscomputes stall_seconds (e.g., due to the `files_changed: 0` bug found in v2.07), the watchdog fires incorrectly.

**Phase status determination**: The spec specifies a 7-level priority chain for `_determine_phase_status()`. The v2.07 retrospective found that "PARTIAL status [is] silently promoted to PASS" because `EXIT_RECOMMENDATION: CONTINUE` overrides `status: PARTIAL` in the priority chain. This means the priority chain was specified but its interaction with EXIT_RECOMMENDATION wasn't validated.

---

## Synthesis

### Top 3 Theories

**Theory 1: The Mock-Reality Chasm**
The diagnostic framework was specified with extraordinary precision (exact log schemas, shell scripts, pytest fixtures) and was presumably implemented against those specifications. But the specifications describe *how the system should behave when working correctly*. They don't describe how the system behaves when Claude produces unexpected output. Every test uses mock/fake claude scripts that produce perfectly formatted output. The first time real Claude output reached the pipeline, it failed. The diagnostic framework can't diagnose problems that its own test infrastructure can't reproduce.

**Theory 2: Specification Precision Creates False Confidence**
Both specs (v2.03 and v2.19) are exceptionally detailed — exact line numbers, regex patterns, acceptance criteria, shell script source code. This precision creates a strong impression of quality. A reviewer reading "R1.7: Every poll loop tick logged with phase, pid, poll_result, elapsed_s, output_bytes, growth_rate_bps, stall_seconds, stall_status" would assess this as thorough and well-thought-out. But specification precision and implementation correctness are orthogonal. A perfectly specified byte-position check is still a brittle byte-position check.

**Theory 3: Diagnostic Framework Tests Its Own Infrastructure, Not the System**
The L0 tests validate that the sprint runner can spawn a subprocess, capture output, parse a result file, and determine pass/fail. But these tests use a *shell script that mimics Claude's expected behavior*. The diagnostic framework tests whether the *test harness* works correctly, not whether the *system under test* handles real-world variability. This is a common testing anti-pattern: testing the scaffolding instead of the product.

### Blind Spots

1. **LLM output format variability**: No spec or test accounts for the possibility that Claude's text-mode output contains preamble, planning text, or non-deterministic formatting. The byte-position frontmatter check assumes clean output.
2. **Schema evolution tracking**: No mechanism exists to detect when the source protocol's schema evolves but the CLI gate definitions don't. Schema drift accumulates silently.
3. **Integration testing with real subprocess**: Every test mocks the Claude subprocess. The pipeline has never been tested with actual Claude output until a user ran it.
4. **Watchdog testing under realistic conditions**: Stall detection is specified but listed as untested in v2.13. The diagnostic framework can't validate something it hasn't tested itself.

### Confidence vs Reality Gaps

| Confidence Claim | Source | Reality |
|------------------|--------|---------|
| "Panel Quality Assessment: 8.6/10" | v2.03 §Panel Quality Assessment | Seven telemetry bugs found on first real run (v2.07) |
| "Overall Grade: B+" | v2.07 §9 | "No criterion was NOT MET" but 6 criteria were PARTIALLY MET with the common gap being "no end-to-end invocation trace" |
| "All failure modes covered" | v2.03 Panel Assessment, Completeness 8.0/10 | `--verbose` stdout pollution not investigated; preamble failure mode not in negative tests |
| "Testability: 9.0/10" | v2.03 Panel Assessment | Tests use fake claude scripts; never validated against real subprocess output |
| "Architecture: 9.0/10" | v2.03 Panel Assessment | Architecture relies on byte-position frontmatter check that fails on real LLM output |

### Evidence Citations

1. v2.19 §1.1: "The pipeline rejects correct work because 53 bytes of LLM conversational preamble precede the `---` delimiter."
2. v2.19 §1.3: "It is unknown whether `--verbose` with `output_format='text'` injects diagnostic text into stdout."
3. v2.03 §R2.1: "Phase task is a shell script (not claude) that writes a properly formatted result file."
4. v2.03 §Panel Quality Assessment: "Testability: 9.0/10" — yet no test uses real Claude output.
5. v2.19 §1.2: "The current CLI extract prompt requests only 3 fields... The gate validates only those 3." — schema drift discovered only on first real run.
6. `pipeline/gates.py` line ~78: `stripped = content.lstrip()` / `if not stripped.startswith("---")` — the actual brittle check still in production code.

---

*Analysis complete. Diagnostic only — no fixes proposed.*
