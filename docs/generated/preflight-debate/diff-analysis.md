# Diff Analysis: Post-Preflight Phase Handling (Q5)

## Variants Under Comparison

| Variant | Label | Summary |
|---------|-------|---------|
| 2a | Skip entirely | Python writes result contract; phase loop skips the phase number; Claude never sees it |
| 2b | Run Claude anyway | Claude subprocess runs but receives pre-computed results as injected context |
| 2c | Configurable | Default to 2a, `--verify-preflight` flag switches to 2b |

---

## Structural Differences

### Control Flow

**2a** inserts a filtering step between `discover_phases()` and the main `for phase in config.active_phases` loop. Phases whose tasks all passed preflight are removed from the iterable (or skipped via `continue`). The result file at `results/phase-N-result.md` is written by Python before the loop starts.

**2b** keeps the loop intact. Every phase still spawns a `claude --print` subprocess, but the prompt is augmented with a structured context block containing pre-computed task outcomes, evidence artifact paths, and a directive to validate rather than re-execute.

**2c** is architecturally identical to 2a in default mode, but adds a `--verify-preflight` CLI flag that switches the code path to 2b for phases that passed preflight. This means both code paths must exist and be maintained.

### Result Contract Authorship

| Aspect | 2a | 2b | 2c |
|--------|----|----|-----|
| Who writes `phase-N-result.md` | Python preflight hook | Claude subprocess | Python (default) or Claude (with flag) |
| YAML frontmatter source | `AggregatedPhaseReport.to_markdown()` or equivalent | Claude's own output | Depends on mode |
| `EXIT_RECOMMENDATION` line | Written by Python | Written by Claude | Depends on mode |
| Evidence artifacts in `artifacts/D-NNNN/` | Produced by preflight shell commands | Referenced/validated by Claude | Depends on mode |

### Code Surface Area

| Metric | 2a | 2b | 2c |
|--------|----|----|-----|
| New functions | ~2 (preflight executor, result writer) | ~3 (preflight executor, context builder, prompt augmenter) | ~4 (all of 2a + 2b + flag routing) |
| Modified functions | `execute_sprint()` (skip logic) | `execute_sprint()` (context injection) | `execute_sprint()` (branching), `load_sprint_config()` (flag), CLI commands |
| New CLI flags | 0 | 0 | 1 (`--verify-preflight`) |
| Test scenarios | Preflight pass, preflight partial pass, result format correctness | Context injection format, Claude validation behavior, prompt length | All of 2a + 2b + flag interaction, default behavior |

---

## Content Differences

### Token/Cost Model

**2a**: Zero Claude tokens consumed for preflight-passing phases. A phase with 5 shell-command tasks that all pass costs 0 API tokens instead of ~5,000-15,000 tokens for a Claude subprocess.

**2b**: Full Claude subprocess cost for every phase, but with potentially shorter runs since Claude receives pre-computed answers. Estimated 60-80% of normal token cost (Claude still reads context, validates, writes report).

**2c**: Defaults to 2a cost profile; `--verify-preflight` activates 2b cost profile.

### Trust Model

**2a**: Full trust in Python's preflight execution. The result contract is authored by deterministic code using `AggregatedPhaseReport.to_markdown()` (which already exists and is tested). No AI verification of outcomes.

**2b**: Trust-but-verify. Python executes tasks, but Claude validates results and can flag discrepancies. Adds a human-readable reasoning layer on top of mechanical execution.

**2c**: User chooses trust level. Default trusts Python; flag enables verification.

---

## Contradictions

1. **2a assumes the result contract is stable enough for Python to author directly.** If the contract format evolves (new fields, changed semantics), Python's writer must be updated in lockstep. 2b avoids this because Claude writes the contract natively.

2. **2b assumes Claude will reliably validate pre-computed results rather than hallucinating alternative conclusions.** Injecting "here are the results, please validate" into a Claude prompt is an untested interaction pattern that could produce unpredictable behavior.

3. **2c claims to be "the best of both worlds" but introduces the combinatorial testing burden of both code paths.** The `--verify-preflight` path may receive less testing and rot faster than the default path.

---

## Unique Contributions

- **2a uniquely offers**: Zero-token execution for mechanical phases; simplest code path; fastest wall-clock time
- **2b uniquely offers**: AI-verified results with reasoning traces; consistent result contract authorship (always Claude)
- **2c uniquely offers**: User agency over trust/cost tradeoff; progressive adoption path; ability to run verification on demand without changing defaults
