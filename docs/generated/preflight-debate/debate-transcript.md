# Adversarial Debate Transcript: Post-Preflight Phase Handling (Q5)

## Debate Parameters
- **Variants**: 2a (Skip entirely), 2b (Run Claude anyway), 2c (Configurable)
- **Dimensions**: Correctness, Cost, Trust, Complexity, User Experience
- **Depth**: Standard (3 rounds)

---

## Round 1: Opening Arguments

### Advocate 2a (Skip Entirely)

**Correctness**: The result contract is already codified in Python. `AggregatedPhaseReport.to_markdown()` (executor.py lines 244-282) produces exactly the format that `_determine_phase_status()` (lines 765-815) parses: YAML frontmatter with `status`, `tasks_total`, `tasks_passed`, the literal `EXIT_RECOMMENDATION: CONTINUE` or `HALT` string, and a per-task status table. This is not a new capability -- it is reusing existing, tested code. Format drift risk is low because both the writer and the parser live in the same codebase and can be updated atomically.

**Cost**: This is the entire point of preflight. If a phase has 5 `execution_mode: python` tasks that all run `uv run pytest tests/unit/` and pass, spawning a Claude subprocess to rubber-stamp the results wastes 5,000-15,000 tokens and 2-5 minutes of wall-clock time. For a 14-phase sprint where 4 phases are mechanical, that is 20,000-60,000 tokens saved per sprint run.

**Trust**: Shell commands either pass (exit 0) or fail (exit non-zero). There is no ambiguity to validate. The preflight hook captures stdout, stderr, and exit codes -- the same evidence Claude would use. Adding an AI layer to verify `exit 0` is over-engineering.

**Complexity**: Two new functions: `run_preflight()` and `write_preflight_result()`. The main loop gets a `if phase.number in preflight_passed: continue` guard. Minimal surface area.

**User Experience**: When preflight fails, the phase is NOT skipped -- it falls back to normal Claude execution. The user sees the same behavior as today for any phase that does not cleanly pass preflight. No new flags to learn.

### Advocate 2b (Run Claude Anyway)

**Correctness**: The result contract is not just a format -- it is a semantic commitment. `_determine_phase_status()` currently parses Claude-authored markdown with case-insensitive regex. The parser is resilient because Claude's output varies. But a Python-authored result file is a different beast: it is deterministic, so any format bug is systematic rather than stochastic. If Python writes `EXIT_RECOMMENDATION: CONTINUE` but the task actually produced a warning that should be reviewed, nobody catches it. Claude, given the evidence, can exercise judgment.

More critically, the result contract may evolve. Today it requires `EXIT_RECOMMENDATION` and YAML frontmatter. Tomorrow it might require a `## Evidence Summary` section, a `confidence_score` field, or cross-phase dependency validation. Claude adapts to contract changes naturally through prompt updates. Python requires code changes, testing, and deployment.

**Cost**: The cost argument for 2a overestimates savings. A Claude subprocess that receives pre-computed results and merely validates them will consume fewer tokens than a from-scratch execution -- estimated 2,000-4,000 tokens vs. 5,000-15,000. The marginal savings of 2a over 2b is ~2,000-4,000 tokens per phase, not 5,000-15,000.

**Trust**: Automated systems should not grade their own homework. The preflight hook both executes tasks AND declares success. This is the same anti-pattern as a CI pipeline that marks itself green without external verification. Claude provides an independent verification layer with different failure modes than the Python runtime.

**Complexity**: The context injection approach adds a `_build_preflight_context()` function and a conditional prompt prefix. This is less complex than it sounds -- the sprint runner already builds prompts for each phase.

**User Experience**: Every phase produces a Claude-authored result file with reasoning. The user can always read the result file and understand WHY the phase passed, not just THAT it passed. With 2a, the result file is a mechanical template with no reasoning.

### Advocate 2c (Configurable)

**Correctness**: 2c eliminates the correctness debate by making it a user choice. The default (skip) is correct for the common case where shell commands are deterministic and the result contract is stable. The `--verify-preflight` flag is correct for the uncommon case where the user wants belt-and-suspenders verification or the result contract has recently changed.

**Cost**: Default behavior saves maximum tokens. Users who want verification opt into the cost explicitly. This is the standard pattern for optional verification (cf. `--shadow-gates` which already exists in `SprintConfig`).

**Trust**: Trust is a spectrum, not a binary. Some users will trust Python's exit codes. Others want AI verification. 2c respects both preferences without imposing either.

**Complexity**: Yes, both code paths must exist. But the 2a path is simple (write result, skip phase) and the 2b path is an additive context injection. The routing logic is a single `if config.verify_preflight:` branch. The `--shadow-gates` flag already demonstrates this pattern in the codebase.

**User Experience**: One new flag (`--verify-preflight`). Follows the existing pattern of `--shadow-gates`, `--stall-timeout`, `--stall-action`. Progressive disclosure: beginners use the default, power users enable verification when needed.

---

## Round 2: Rebuttals

### 2a rebuts 2b

The "grading your own homework" analogy is flawed. The preflight hook does not grade -- it executes and reports exit codes. The grading is done by `_determine_phase_status()`, which is the same function that grades Claude's output today. The parser does not care who wrote the file; it applies the same regex logic.

On contract evolution: if the result contract changes, `_determine_phase_status()` must change too. At that point, both the parser and the writer are in Python and can be updated atomically. Claude's "natural adaptation" is actually a liability -- Claude might produce a result file that satisfies a new contract field by hallucinating a value, while Python would fail loudly with a missing field.

On cost: 2,000-4,000 tokens per phase is still 8,000-16,000 tokens wasted per sprint for rubber-stamping. Over hundreds of sprint runs during development, this adds up to meaningful cost and time.

### 2b rebuts 2a

The "fail loudly with a missing field" argument cuts both ways. If Python fails to write a required field, the sprint halts with an obscure error in `_determine_phase_status()`. The user sees `PhaseStatus.PASS_NO_SIGNAL` or `PhaseStatus.ERROR` and has no idea why -- because the diagnostic assumes Claude wrote the file. The error reporting pipeline (diagnostics, failure classification) is designed around Claude subprocess failures, not Python writer bugs.

On exit codes: exit 0 does not mean "correct." A test suite can pass while having regressions that the tests do not cover. Claude, reading the actual test output, can flag suspicious patterns (e.g., "0 tests ran" or "all tests skipped"). Python's preflight hook would need to implement these heuristics in code -- which is exactly the kind of judgment work Claude excels at.

### 2c rebuts both

Both 2a and 2b are making absolutist claims about a tradeoff that is inherently contextual. The correct answer depends on: how mature the result contract is (stable = 2a is fine), how critical the sprint is (production release = 2b is prudent), and how experienced the user is (novice = 2a default is safer).

2c is not "both code paths are equally maintained." The default path (2a/skip) gets 95% of the usage and testing. The verification path (2b) is an escape hatch that exists for edge cases. This is the same pattern as `--debug` or `--dry-run` -- secondary paths that serve important but infrequent use cases.

### 2a rebuts 2c

The `--shadow-gates` analogy is misleading. Shadow gates are a parallel, non-blocking evaluation -- they never affect sprint behavior. `--verify-preflight` would change the execution path, output format, and cost profile. This is a more consequential flag that introduces a maintenance burden disproportionate to its value.

Furthermore, 2c's "escape hatch" framing acknowledges that the 2b path will receive less testing. An undertested escape hatch is worse than no escape hatch -- it gives users false confidence that verification is working when it might be broken.

---

## Round 3: Convergence

### Points of Agreement

| Point | 2a | 2b | 2c | Convergence |
|-------|----|----|-----|-------------|
| Preflight should execute `execution_mode: python` tasks in Python before the main loop | Agree | Agree | Agree | 100% |
| Python can reliably capture exit codes, stdout, stderr from shell commands | Agree | Agree | Agree | 100% |
| `AggregatedPhaseReport.to_markdown()` produces a parseable result contract | Agree | Agree (but insufficient alone) | Agree | 90% |
| Token savings from skipping Claude are meaningful (>5K tokens/phase) | Agree | Disagree (overestimated) | Agree for default | 67% |
| The result contract format is currently stable | Agree | Disagree (will evolve) | Partially agree | 67% |
| Preflight failure should fall back to normal Claude execution | Agree | N/A (always runs Claude) | Agree for default | 100% |
| Exit 0 is sufficient evidence of task success for mechanical tasks | Agree | Disagree (edge cases) | Agree for default | 67% |
| An untested verification path is worse than none | Agree | Disagree | Partially agree | 50% |

### Points of Disagreement (Irreducible)

1. **Contract authorship responsibility**: 2a says Python is the right author for deterministic results. 2b says Claude should always author to maintain contract consistency. This is a philosophical difference about where the source of truth for result semantics lives.

2. **Value of AI verification for mechanical tasks**: 2a says exit codes are sufficient. 2b says Claude adds judgment value. Neither side can prove the marginal value of Claude's verification without empirical data from production sprint runs.

3. **Maintenance cost of dual paths**: 2a and 2b agree this is a burden. 2c says it is manageable. Without historical data on code path usage, this is speculative.

---

## Per-Point Scoring Matrix

| Dimension | 2a | 2b | 2c | Reasoning |
|-----------|----|----|-----|-----------|
| **Correctness** | 8/10 | 7/10 | 7/10 | 2a reuses tested code. 2b risks prompt injection issues. 2c inherits both risks. |
| **Cost** | 10/10 | 4/10 | 9/10 | 2a saves all tokens. 2b saves none. 2c defaults to 2a. |
| **Trust** | 7/10 | 9/10 | 8/10 | 2b provides independent verification. 2a trusts deterministic code. 2c lets user choose. |
| **Complexity** | 9/10 | 6/10 | 5/10 | 2a is simplest. 2b is moderate. 2c has dual-path burden. |
| **User Experience** | 8/10 | 7/10 | 7/10 | 2a is invisible. 2b adds reasoning. 2c adds a flag. |
| **Weighted Total** | **8.4** | **6.6** | **7.2** | Weights: Correctness(0.25), Cost(0.20), Trust(0.20), Complexity(0.20), UX(0.15) |

### Convergence Assessment

Overall convergence: **72%** -- agreement on execution mechanics, disagreement on verification value and maintenance burden.
