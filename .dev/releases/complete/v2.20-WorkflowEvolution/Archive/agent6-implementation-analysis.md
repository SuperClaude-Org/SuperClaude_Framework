# Agent 6: Implementation Analysis — Roadmap CLI

**Date**: 2026-03-08
**Scope**: Compare actual `src/superclaude/cli/roadmap/` implementation against `v2.08-RoadmapCLI/merged-spec.md`
**Mode**: Diagnostic only — no fix proposals

---

## 1. Top 3 Theories for Why Bugs Survive the Workflow Despite Planning Rigor

### Theory 1: Prompt-Level Structural Compliance ≠ Semantic Effectiveness (The "Letter vs. Spirit" Gap)

The implementation faithfully reproduces every structural element the spec demands — YAML frontmatter fields, line counts, heading hierarchies — while leaving the actual *content quality* of LLM outputs entirely unvalidated. The gates check *form* (does the file have `convergence_score`?) but never *substance* (does the convergence score reflect the actual debate content?).

**Evidence**:

- `gates.py` `_cross_refs_resolve()` (lines ~40-60) explicitly gives up on real validation: `# Don't fail on this -- it's too fragile for now` followed by `return True`. The function finds cross-references, iterates over them, but **unconditionally returns True**. The spec (§4, Semantic checks for STRICT-tier steps) lists `cross_refs_resolve` as: *"All 'See §X' and 'Section X.Y' references resolve to existing headings"*. The implementation acknowledges this is needed but defers enforcement indefinitely.

- `_convergence_score_valid()` checks only that the value parses as a float in [0.0, 1.0]. The LLM can write `convergence_score: 0.5` with no relationship to the actual debate content. The spec's design principle (§1) states: *"the same model that produces output cannot reliably validate its own intermediate state"*, yet the convergence score — produced and self-reported by the same model — is trusted at face value.

- `_has_actionable_content()` checks for the mere *existence* of a single bullet or numbered item (`re.search(r'^\s*(?:[-*]|\d+\.)\s+\S', ...)`). A roadmap with one bullet point and 99 lines of placeholder prose passes this gate. The spec intended (§4) that generate steps would contain meaningful *"phased implementation plan with milestones, risk assessment and mitigation strategies"* etc.

**Why this survives the workflow**: The spec itself is precise about structural requirements but imprecise about content requirements. The spec meticulously defines frontmatter fields and line counts (§4 table), but the actual prompt instructions in §13.3 are vague directives like *"Be thorough and precise"* and *"Be specific and concrete"*. The implementation is faithful to both the structured and unstructured parts of the spec — the problem is that the unstructured parts were never checkable by pure-Python gates in the first place.

---

### Theory 2: Input Embedding Bypasses Context Isolation Contract (The "Inline vs. --file" Divergence)

The spec mandates strict context isolation (§3.4, FR-03): *"Each step receives its context exclusively through the prompt string and the --file flags passed to claude -p."* The implementation introduces a major undocumented deviation: the `_embed_inputs()` function in `executor.py` (lines ~35-55) reads input files and inlines their full content into the prompt string, only falling back to `--file` flags when embedded content exceeds 100KB.

**Evidence**:

- `roadmap/executor.py` `roadmap_run_step()` (lines ~75-95):
  ```python
  embedded = _embed_inputs(step.inputs)
  if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
      effective_prompt = step.prompt + "\n\n" + embedded
      extra_args: list[str] = []
  elif embedded:
      ...
      extra_args = [arg for input_path in step.inputs for arg in ("--file", str(input_path))]
  ```
  This means for typical pipeline runs (where individual artifacts are <100KB), **no `--file` flags are ever passed**. All context is crammed into the prompt string.

- The spec's subprocess invocation pattern (§3.4) is explicit:
  ```
  claude -p "<step.prompt>" \
    --file <input_1> \
    --file <input_2> \
    --model <agent.model> ...
  ```
  The implementation's `_embed_inputs()` approach is nowhere in the spec. The spec's §13.3 `_build_subprocess_argv()` function shows `--file` injection as the canonical pattern.

- The `prompts.py` functions accept `Path` arguments (e.g., `build_diff_prompt(variant_a_path, variant_b_path)`) but **never use them** — they don't read the files or reference the paths in the prompt text. The paths are dead parameters. The prompt text says *"Read the provided specification file"* and *"Read the two provided roadmap variants"* but never says *which* file — because the executor separately handles file delivery. This creates a fragile contract: the prompt says "read the provided X" but whether X arrives via `--file` or inline embedding is an invisible executor-level decision.

**Why this survives the workflow**: The embedding approach is a reasonable engineering optimization (avoiding `--file` flag limitations), but it was implemented without updating the spec. The spec review process checked the spec's *stated* architecture, not the *actual* code. Nobody verified that `_build_subprocess_argv()` from §13.3 was actually used.

---

### Theory 3: State Management Deviates From Spec Schema, Creating Resume Fragility

The `.roadmap-state.json` implementation diverges from the spec's defined schema (§13.4) in several ways that make `--resume` behavior unreliable.

**Evidence**:

- **Missing fields**: The spec schema (§13.4) requires `pipeline_started_at`, `updated_at`, and per-step `gate_failure_reason`. The actual `_save_state()` implementation (executor.py, lines ~210-235) writes:
  ```python
  state = {
      "schema_version": 1,
      "spec_file": str(config.spec_file),
      "spec_hash": spec_hash,  # raw hex, not "sha256:" prefixed
      "agents": [...],
      "depth": config.depth,
      "last_run": datetime.now(timezone.utc).isoformat(),  # spec says "updated_at"
      "steps": { r.step.id: { "status": ..., "attempt": ..., ... } }
  }
  ```
  Field `spec_hash` uses raw hex (`hashlib.sha256(...).hexdigest()`) while the spec says `"sha256:a1b2c3d4e5f6..."`. Field naming: `last_run` instead of `updated_at`; `attempt` instead of `attempts`; `completed_at` instead of `finished_at`. No `pipeline_started_at` or per-step `gate_failure_reason`.

- **State written only at pipeline end**: The spec (§13.4) says the state file is *"Updated after each step completes"*. The implementation calls `_save_state()` only once, after the entire pipeline finishes (executor.py `execute_roadmap()`, line ~280). If the pipeline crashes mid-execution, no state is saved. This makes `--resume` useless after a process crash (as opposed to a gate failure).

- **Resume doesn't use state file for skip logic**: The `_apply_resume()` function (executor.py, lines ~300-360) only reads the state file for stale-spec detection. Skip decisions are made by re-running `gate_fn(s.output_file, s.gate)` on existing output files. While this is functionally correct, it means the state file is mostly write-only ceremony — the spec designed it as the resume mechanism, but the implementation bypasses it for the core skip logic.

**Why this survives the workflow**: The state file schema was specified in great detail (§13.4), but no acceptance test verifies schema conformance. AC-04 and AC-05 test skip/re-run behavior but not the state file's contents. The implementation correctly implements the *behavior* of resume (skip steps with passing gates) while implementing the *mechanism* differently than specified (gate re-evaluation instead of state file lookup).

---

## 2. Blind Spots — What the Workflow Systematically Fails to Examine

### Blind Spot A: Dead Code and Vestigial Parameters

The prompt builder functions in `prompts.py` all accept `Path` parameters that are never used. For example:

```python
def build_extract_prompt(spec_file: Path) -> str:
    # spec_file is never referenced in the returned string
    return (
        "You are a requirements extraction specialist.\n\n"
        "Read the provided specification file and produce..."
    )
```

Every prompt builder (`build_extract_prompt`, `build_generate_prompt`, `build_diff_prompt`, etc.) takes paths but doesn't use them. The spec's §13.3 describes these as *"pure functions: takes concrete values, returns str, performs no I/O"* — but the concrete values passed are ignored. The functions would produce identical output regardless of which paths are passed. This means:
- A test can call `build_extract_prompt(Path("/nonexistent"))` and get a valid prompt
- The prompt-to-input-file contract is never verified at the function level

### Blind Spot B: Parallel Step Gate Checking Omission

In `pipeline/executor.py`, `_run_parallel_steps()` calls `_execute_single_step()` for each parallel step, which does include gate checking. However, when `_run_parallel_steps()` is called from `execute_pipeline()`, the parallel group's results are checked only for `status != StepStatus.PASS`:

```python
# pipeline/executor.py, execute_pipeline():
group_results = _run_parallel_steps(entry, config, run_step, cancel_check)
...
if any(r.status != StepStatus.PASS for r in group_results):
    break
```

But `_execute_single_step()` inside the parallel worker doesn't call `on_step_start()` — that's done at the `execute_pipeline` level before the parallel group launches. This means `on_step_start` is called for all parallel steps simultaneously *before* any of them execute, which is semantically correct for display but could be confusing if `on_step_start` has side effects.

### Blind Spot C: No Validation That LLM Output Matches Prompt Instructions

The entire gate system validates structural output properties (frontmatter, line counts, heading structure) but never validates that the output *responds to the prompt's instructions*. For example:
- The merge prompt says *"Use the selected base variant as foundation"* — no gate verifies the base variant was actually used
- The debate prompt says *"Conduct two debate rounds"* (standard depth) — no gate verifies that two rounds appear in the output
- The score prompt says *"Score each variant"* — no gate verifies that both variants received scores

This is acknowledged by the spec's design principle (§1): *"Gate validation is pure Python — it never invokes Claude to evaluate Claude's output."* But the consequence is that gates catch only *structural* fabrication (missing fields, short files), not *semantic* fabrication (copying one variant as the merge output without actual synthesis).

### Blind Spot D: The `max_turns` Default Diverges Between Spec and Implementation

The spec (§5) specifies `--max-turns INT` with *"Default: 50"*. The `commands.py` implementation defaults to `max_turns=100`. The `PipelineConfig` also defaults to `100`. The spec (§3.2) shows `PipelineConfig` with `max_turns: int = 50`. This is a straightforward discrepancy that was never caught because no test asserts the default value.

---

## 3. Confidence vs. Reality Gaps

### Gap 1: Semantic Checks Appear Rigorous But Are Partially No-Ops

The gate definitions in `roadmap/gates.py` define semantic checks that *look* comprehensive — `_cross_refs_resolve`, `_no_heading_gaps`, `_no_duplicate_headings`, `_convergence_score_valid`, `_frontmatter_values_non_empty`, `_has_actionable_content` — but several are effectively pass-through:

- `_cross_refs_resolve()` unconditionally returns `True` (see Theory 1 evidence)
- `_has_actionable_content()` requires only one bullet point in the entire file
- `_frontmatter_values_non_empty()` checks YAML values are non-empty strings, but the LLM can write `complexity_score: placeholder` and pass

A code reviewer seeing six semantic checks on STRICT-tier gates would *perceive* thorough validation. The reality is that only `_no_heading_gaps()`, `_no_duplicate_headings()`, and `_convergence_score_valid()` provide meaningful constraint.

### Gap 2: Spec Claims 8-Step Pipeline; Implementation Has 7 Steps

The spec abstract (§1, §2) describes an *"8-step pipeline"*, and the `__init__.py` docstring says *"orchestrate an 8-step pipeline"*. The `commands.py` docstring says *"Orchestrates an 8-step pipeline: extract, generate (x2 parallel), diff, debate, score, merge, and test-strategy."* That's 7 distinct steps where generate runs twice in parallel. The spec's §4 step definition table also lists 7 IDs (counting both generate variants as one row with "(×2, parallel)"). The `_build_steps()` function creates 7 top-level entries (one of which is a list of 2 parallel steps = 8 total subprocess invocations). The "8" is inconsistently used to mean either 8 subprocess invocations or 7 logical steps, creating confusion in diagnostics. The `_format_halt_output()` uses `_get_all_step_ids()` which returns 8 IDs, while `_dry_run_output()` prints "Step N" with inconsistent numbering.

### Gap 3: Context Isolation Claimed But Not Enforced

The spec's §3.4 states: *"Each step receives its context exclusively through the prompt string and the --file flags."* The executor's docstring (lines 1-7) claims: *"Context isolation: each subprocess receives only its prompt and --file inputs. No --continue, --session, or --resume flags are passed (FR-003, FR-023)."*

But the `_embed_inputs()` mechanism (Theory 2) means context delivery is actually through inline embedding, not `--file` flags. The `ClaudeProcess.build_command()` includes `--no-session-persistence` and avoids `--continue`, so session isolation is enforced — but the input delivery mechanism diverges from spec. The claim is *partially* true (no session leakage) but *partially* false (no `--file` usage in the common path).

### Gap 4: The `apply_decomposition_pass()` Function Exists But Is Never Called in the Pipeline

`executor.py` defines `apply_decomposition_pass()` (lines ~245-260) which imports and wraps `decompose_deliverables()` from the pipeline module. This function is defined, documented, and imported, but is **never invoked** anywhere in the roadmap execution path. `execute_roadmap()` doesn't call it; `_build_steps()` doesn't call it; no step's gate or post-processing calls it. It's dead code that suggests a planned feature (deliverable decomposition) was spec'd but never wired into the pipeline.

---

## 4. Evidence Citations

### From `roadmap/gates.py`:

**_cross_refs_resolve — unconditional pass**:
```python
for ref in refs:
    found = any(ref in h for h in headings)
    if not found:
        found = any(h.startswith(ref) for h in headings)
    # Don't fail on this -- it's too fragile for now
return True
```
This function is assigned to `MERGE_GATE`'s `semantic_checks` list, meaning the STRICT-tier merge gate runs this check but it can never fail.

**_has_actionable_content — minimal threshold**:
```python
def _has_actionable_content(content: str) -> bool:
    return bool(re.search(r'^\s*(?:[-*]|\d+\.)\s+\S', content, re.MULTILINE))
```
One bullet point anywhere in the file satisfies this for a STRICT gate on a full roadmap.

### From `roadmap/executor.py`:

**Input embedding overrides --file pattern**:
```python
_EMBED_SIZE_LIMIT = 100 * 1024  # 100 KB

def _embed_inputs(input_paths: list[Path]) -> str:
    ...
    blocks.append(f"# {p}\n```\n{content}\n```")
    ...

# In roadmap_run_step():
embedded = _embed_inputs(step.inputs)
if embedded and len(embedded.encode("utf-8")) <= _EMBED_SIZE_LIMIT:
    effective_prompt = step.prompt + "\n\n" + embedded
    extra_args: list[str] = []
```
This deviates from spec §3.4 and §13.3 which define `--file` injection as the delivery mechanism.

**State saved once at end, not per-step**:
```python
def execute_roadmap(config: RoadmapConfig, resume: bool = False) -> None:
    ...
    results = execute_pipeline(...)
    _save_state(config, results)  # Only here, after pipeline completes
```
Spec §13.4: *"Updated after each step completes — not only after extract."*

### From `roadmap/commands.py`:

**max_turns default divergence**:
```python
@click.option(
    "--max-turns",
    type=int,
    default=100,  # Spec §5 says "Default: 50"
    ...
)
```

### From `roadmap/prompts.py`:

**Dead Path parameters** (all 7 builders):
```python
def build_extract_prompt(spec_file: Path) -> str:
    # spec_file never referenced in returned string
    return ("You are a requirements extraction specialist.\n\n" ...)

def build_diff_prompt(variant_a_path: Path, variant_b_path: Path) -> str:
    # Neither path referenced in returned string
    return ("You are a comparative analysis specialist.\n\n" ...)
```

### From `merged-spec.md`:

**Spec §1 — design principle**:
> *"Gate validation (gate_passed()) is pure Python — it never invokes Claude to evaluate Claude's output. This eliminates the circular self-validation failure mode where the same model that produced an artifact judges its own quality."*

This principle is correctly implemented in `pipeline/gates.py`. But the consequence — that gates can only check structure, not content quality — is the root of Theory 1.

**Spec §3.4 — context isolation**:
> *"Each step receives its context exclusively through the prompt string and the --file flags passed to claude -p."*

Violated by `_embed_inputs()` in the common path (Theory 2).

**Spec §13.4 — state update frequency**:
> *"Updated after each step completes — not only after extract."*

Implementation updates only after full pipeline completion (Theory 3).

**Spec §5 — max-turns default**:
> *"--max-turns INT: Max turns passed to each claude -p invocation. Default: 50"*

Implementation uses `default=100` in `commands.py`.

---

## Summary of Diagnostic Findings

| # | Category | Finding | Severity |
|---|----------|---------|----------|
| T1 | Spec-Impl Gap | Gates check form, never substance; semantic checks partially no-ops | High |
| T2 | Spec-Impl Gap | Input embedding bypasses `--file` pattern; undocumented deviation | Medium |
| T3 | Spec-Impl Gap | State file schema diverges; written once not per-step; resume uses gate re-evaluation not state | Medium |
| B-A | Blind Spot | Prompt builder Path parameters are dead code | Low |
| B-B | Blind Spot | `on_step_start` called for all parallel steps before any execute | Low |
| B-C | Blind Spot | No content-quality validation possible under pure-Python gate constraint | High |
| B-D | Blind Spot | `max_turns` default diverges (100 vs spec's 50) | Low |
| C1 | Confidence Gap | 6 semantic checks look thorough; 3 are effectively no-ops or minimal | High |
| C2 | Confidence Gap | "8-step pipeline" numbering inconsistency in docs and code | Low |
| C3 | Confidence Gap | Context isolation claimed but delivery mechanism differs from spec | Medium |
| C4 | Confidence Gap | `apply_decomposition_pass()` defined but never called; dead code | Low |
