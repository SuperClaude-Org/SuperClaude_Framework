# 04 — Pipeline Unification Spec + Implementation Analysis

**Scope**: v2.13 CLIRunner Pipeline Targeted Fixes spec + actual implementation in `src/superclaude/cli/roadmap/`
**Focus**: Architecture & Quality — spec promises vs code reality
**Date**: 2026-03-08
**Purpose**: Diagnostic only — no fixes proposed

---

## Part 1: Pipeline Unification Spec Analysis (v2.13)

### Integration Assumptions Never Validated

**Assumption 1: Hook callbacks won't alter timing or behavior.**

The v2.13 spec introduces lifecycle hooks (`on_spawn`, `on_exit`, `on_signal`) to replace Sprint's method overrides. The spec explicitly documents 5 edge cases (§9.6) — but frames them as acceptable rather than testable:

> "If `on_signal('SIGTERM', pid)` raises, the SIGKILL escalation path is skipped. This is **acceptable** — a buggy hook should surface loudly, and the process will be orphaned."

**Assessment**: The spec converts method overrides (which have full access to object state) into callbacks (which receive limited parameters). Edge Case 3 acknowledges that `was_timeout` information is lost in the hook signature. The spec accepts this loss: "Sprint's debug_log `was_timeout` field is informational only — it doesn't drive control flow." But this is an assumption about *current* usage. Future code that reads `was_timeout` would silently receive wrong data.

**Assumption 2: Sprint tests are a reliable regression baseline.**

The spec states: "All sprint test files passing at extraction start are not modified during pipeline/ migration." But v2.07 already modified 9 of 14 sprint test files. The v2.13 spec further notes "Sprint executor test coverage is approximately 45%." A 45% coverage regression baseline means 55% of behavior changes would be undetected.

**Assumption 3: Dead code deletion is safe because grep found zero references.**

D2 deletes `_build_subprocess_argv()` based on `grep -r` finding zero call sites. But `grep -r` doesn't find dynamic references (e.g., `getattr(module, "_build_subprocess_argv")`), nor does it find references from test files, documentation, or other specs that reference this function by name. The v2.13 spec's own existence references the function — what if other specs or docs reference it as part of the architecture?

### Happy-Path Bias

The spec describes D3 (file-passing fix) with a clean implementation:

```python
def _embed_inputs(prompt: str, inputs: list[Path]) -> str:
    if not inputs:
        return prompt
    parts = [prompt, "\n\n## Input Files\n"]
    for path in inputs:
        content = path.read_text(encoding="utf-8")
        parts.append(f"\n### {path.name}\n```\n{content}\n```\n")
    return "".join(parts)
```

**Missing edge cases**:
- What if an input file doesn't exist? (No try/except around `read_text`)
- What if an input file is binary? (No encoding error handling)
- What if the file content itself contains ` ``` ` fence markers? (Nested fences break markdown)
- What if two input files have the same `path.name`? (Headers would be ambiguous)

The spec addresses one edge case: "If total embedded content exceeds 100KB, fall back to `--file` flags with a warning." This is the only error handling specified.

### Unification Increasing Coupling

The pipeline extraction created an inheritance hierarchy:
- `PipelineConfig` → extended by `SprintConfig` and `RoadmapConfig`
- `ClaudeProcess` → extended by Sprint's `ClaudeProcess`
- `Step` → used directly by both sprint and roadmap

This coupling means:
1. Changes to `PipelineConfig` fields affect both sprint and roadmap
2. Changes to `ClaudeProcess.start()` behavior affect both consumers
3. Changes to `Step` semantics (e.g., making `gate` required) break sprint

The v2.13 spec acknowledges this: "NFR-007: pipeline has zero imports from sprint or roadmap." But the coupling flows the other way — sprint and roadmap both import from pipeline. A change in pipeline propagates to both consumers. The spec enforces one direction of isolation but not the other.

---

## Part 2: CLI Roadmap Implementation Analysis

### Spec-to-Code Comparison

**Models (models.py — 62 lines)**:
- `AgentSpec` and `RoadmapConfig` match the v2.08 merged spec closely.
- `RoadmapConfig` extends `PipelineConfig` as specified.
- Default agents are `opus:architect` and `haiku:architect` as specified.
- **Gap**: No validation that `agents` list has at least one element. `_build_steps` accesses `config.agents[0]` without bounds checking.

**Executor (executor.py — 596 lines)**:
- `roadmap_run_step()` implements the subprocess lifecycle as specified.
- `_embed_inputs()` implements the D3 file-passing fix from v2.13.
- **Critical code pattern**: The poll loop after `proc.start()`:

```python
while proc._process is not None and proc._process.poll() is None:
    if cancel_check():
        proc.terminate()
        return StepResult(...)
    time.sleep(1)
exit_code = proc.wait()
```

This accesses `proc._process` (a private attribute) and calls `proc.wait()` after the process has *already exited* (the poll loop only breaks when `poll()` returns non-None, meaning the process has terminated). The `proc.wait()` call is redundant but harmless — unless `wait()` has side effects (closing file handles) that need to happen in the right order.

**More critically**: Between the poll loop ending (process exited) and `proc.wait()` being called, there's no error handling. If `proc.wait()` raises an exception (e.g., file handle already closed), the step result is never returned.

**Gates (gates.py — 247 lines)**:
- All 8 gate definitions match the spec's requirements.
- Semantic check functions are well-implemented.
- **Gap in `_frontmatter_values_non_empty()`**: This function checks frontmatter values are non-empty, but it assumes frontmatter starts at the beginning of the file:

```python
stripped = content.lstrip()
if not stripped.startswith("---"):
    return False
```

This is the SAME byte-position assumption that the reliability spec (v2.19) identifies as the root cause of pipeline failure. The semantic check functions in `roadmap/gates.py` replicate the bug that `pipeline/gates.py` has. If the pipeline gate (using the regex fix from v2.19) passes, but the semantic check (still using `startswith("---")`) fails, the gate reports a semantic check failure that's actually a frontmatter parsing issue.

**Same issue in `_convergence_score_valid()`**:
```python
stripped = content.lstrip()
if not stripped.startswith("---"):
    return False
```

Both semantic check functions independently parse frontmatter using the brittle method, even though the gate function will use the (eventually fixed) pipeline-level `_check_frontmatter()`. This creates a race condition: fix the pipeline gate, but the semantic checks still fail on preamble.

**Prompts (prompts.py — 223 lines)**:
- All 7 prompt builders are pure functions as specified.
- Prompts include `"Your output MUST begin with YAML frontmatter delimited by --- lines"` format anchoring.
- **Gap**: The extract prompt says `"Read the provided specification file"` but the prompt function doesn't reference the spec file's *content* — it's expected to be passed via `--file` flags or inline embedding by the executor. The prompt refers to "the provided specification file" generically. If the embedding fails silently, Claude would have no input to extract from.
- **Gap**: The prompts specify frontmatter field names (e.g., `functional_requirements`, `complexity_score`) but don't specify the field format. `complexity_score` is expected to be a float, but the prompt says "float 0.0-1.0 assessing overall complexity" without a strict format constraint. Claude could produce `complexity_score: "approximately 0.7"` and the gate would check for field *presence* but not *type*.
- **Gap**: Prompts don't specify output length expectations. The extract gate requires `min_lines: 50`, but the prompt doesn't tell Claude "your response should be at least 50 lines." This creates a silent failure mode where Claude produces a concise 30-line extraction that passes all quality checks except the line count gate.

**Commands (commands.py — 119 lines)**:
- Click command group and options match the merged spec.
- **Gap**: `--max-turns` defaults to 100, but the v2.05 sprint spec uses 50 as default. This inconsistency means roadmap and sprint have different timeout behaviors for the same underlying Claude subprocess.

### Code Patterns Suggesting Generation Without Full Spec Context

**Pattern 1: Defensive fallback that contradicts the spec.**

```python
agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]
```

The merged spec says "v1 supports exactly 2 agents for generate-A / generate-B." But the code silently falls back to using the same agent for both variants if only one is provided. The spec never describes this behavior — the code is defensively handling a case the spec says shouldn't occur. This suggests the implementer anticipated a problem the spec didn't address.

**Pattern 2: Private attribute access.**

```python
while proc._process is not None and proc._process.poll() is None:
```

Accessing `_process` (a private attribute of `ClaudeProcess`) breaks encapsulation. The spec defines `ClaudeProcess` with `start()`, `wait()`, and `terminate()` as the public interface. The executor reaches into the private `_process` attribute for the poll loop, suggesting the implementer needed functionality the public API didn't provide.

**Pattern 3: Import from non-existent module.**

```python
from ..pipeline.deliverables import decompose_deliverables
from ..pipeline.models import Deliverable, ...
```

The executor imports `Deliverable` and `decompose_deliverables` from `pipeline.deliverables`. These types are not defined in any spec I've reviewed, and the function `apply_decomposition_pass()` that uses them is never called from `execute_roadmap()`. This appears to be dead code from a feature that was partially implemented or planned but not completed.

**Pattern 4: Redundant `wait()` after poll loop.**

The poll loop waits for the process to exit, then calls `proc.wait()` which waits again. This is technically safe but suggests the implementer wasn't certain whether `poll()` completing meant all cleanup was done.

### Error Handling Gaps

| Location | Gap |
|----------|-----|
| `_embed_inputs()` | No try/except around `Path(p).read_text()` — fails on missing/binary files |
| `roadmap_run_step()` | No handling of `proc.start()` exceptions (e.g., `claude` binary not found) |
| `_build_steps()` | No validation of `config.agents` length — crashes on empty list |
| `_apply_resume()` | `config.spec_file.read_bytes()` for hash — crashes if spec_file doesn't exist |
| `_save_state()` | `config.spec_file.read_bytes()` for hash — same issue |
| `_format_halt_output()` | `step.output_file.read_text()` — could fail on binary content |
| All semantic checks | Parse frontmatter with `startswith("---")` — replicates the preamble bug |

### Untested Code Paths

| Code Path | Test Coverage |
|-----------|--------------|
| Real Claude subprocess execution | Never tested — mocked |
| `_embed_inputs()` with large files (>100KB) | Fallback to `--file` flags untested |
| `_apply_resume()` with stale spec | Hash comparison untested with real files |
| `_format_halt_output()` | Error formatting untested |
| `apply_decomposition_pass()` | Function exists but is never called |
| Semantic checks on files with preamble | Frontmatter parsing assumes no preamble |
| `cancel_check()` during subprocess | Cancellation path untested |

---

## Synthesis

### Top 3 Theories

**Theory 1: The Implementation Was Generated from Prompt Context, Not Full Spec Understanding**
Multiple code patterns — defensive fallbacks for cases the spec excludes, private attribute access to work around API limitations, dead imports from unspecified modules, redundant operations — suggest the implementation was generated by an agent that had prompt-level access to requirements but not deep understanding of the design intent. The code works for the happy path but diverges from the spec's architectural vision in subtle ways.

**Theory 2: Semantic Check Functions Replicate the Pipeline Bug**
The reliability spec (v2.19) identifies and fixes the byte-position frontmatter check in `pipeline/gates.py`. But `roadmap/gates.py` contains TWO semantic check functions (`_frontmatter_values_non_empty` and `_convergence_score_valid`) that independently implement the same brittle parsing: `content.lstrip().startswith("---")`. Fixing the pipeline gate without fixing the semantic checks creates a false floor: the gate passes (regex-based), then the semantic check fails (byte-position-based). The bug survives the fix because the fix is applied to one layer while the bug exists in another.

**Theory 3: Pipeline Unification Creates Shared Liability Without Shared Testing**
The pipeline extraction created shared infrastructure (`pipeline/process.py`, `pipeline/gates.py`, `pipeline/executor.py`) used by both sprint and roadmap. But the test suites are separate (`tests/sprint/`, `tests/roadmap/`). A change to pipeline affects both consumers, but only one test suite might catch the regression. The v2.13 spec's "characterization tests" (D4) target sprint's executor only, leaving roadmap's usage of the shared pipeline untested at the integration level.

### Blind Spots

1. **Semantic checks parse frontmatter independently**: Each semantic check function re-implements frontmatter extraction instead of using the gate's parsed frontmatter. This means fixing the gate doesn't fix the checks.
2. **Dead code / unused imports**: `apply_decomposition_pass()` and `Deliverable` imports exist in production code but are never called. Nobody noticed because there are no tests for unused code detection.
3. **Private attribute access**: The executor accesses `proc._process` directly, bypassing the `ClaudeProcess` public API. This creates a fragile dependency on implementation details.
4. **Prompt-gate misalignment**: Prompts tell Claude what fields to produce but not the exact format. Gates check field *presence* but not field *type*. Claude can produce a valid-looking but type-incorrect frontmatter that passes all gates.

### Confidence vs Reality Gaps

| Confidence Claim | Source | Reality |
|------------------|--------|---------|
| "Option 3 — Targeted Fixes" framed as low-risk | v2.13 §1 | D3 (file-passing fix) introduces `_embed_inputs()` without error handling |
| "Estimated Reduction: ~70 lines removed" | v2.13 §D1 | Lines removed, but hook protocol adds behavioral complexity |
| "AC-5: NFR-007 remains satisfied" | v2.13 §D1 | NFR-007 enforces one-directional isolation; coupling flows the other way |
| "Sprint executor test coverage >= 70%" | v2.13 §10 | Target for sprint only; roadmap coverage unspecified |
| EXTRACT_GATE validates pipeline output | roadmap/gates.py | Validates 3 fields; source protocol requires 17+ |
| "No heading gaps" semantic check | roadmap/gates.py | Correctly implemented — but only checks *output* documents, not whether content is *correct* |

### Evidence Citations

1. `roadmap/gates.py` `_frontmatter_values_non_empty()`: `stripped = content.lstrip()` / `if not stripped.startswith("---"): return False` — replicates the pipeline/gates.py preamble bug.
2. `roadmap/executor.py` line ~118: `while proc._process is not None and proc._process.poll() is None:` — private attribute access.
3. `roadmap/executor.py` line ~18: `from ..pipeline.deliverables import decompose_deliverables` — import from module not in any spec.
4. `roadmap/prompts.py` `build_extract_prompt()`: "Read the provided specification file" — no reference to how the file content reaches Claude.
5. v2.13 §9.6 Edge Case 3: "The hook factory uses `returncode == 124` as the timeout indicator... Accept `was_timeout=(returncode == 124)` in the hook." — information loss accepted as design tradeoff.
6. `roadmap/executor.py` `_build_steps()`: `agent_b = config.agents[1] if len(config.agents) > 1 else config.agents[0]` — defensive fallback not in spec.

---

*Analysis complete. Diagnostic only — no fixes proposed.*
