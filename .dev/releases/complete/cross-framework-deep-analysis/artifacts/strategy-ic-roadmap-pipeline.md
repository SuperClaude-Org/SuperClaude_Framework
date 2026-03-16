---
component: roadmap-pipeline
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
---

# Strategy: IronClaude Roadmap Pipeline

## 1. Design Philosophy

The roadmap pipeline exists to eliminate LLM output variance when generating project roadmaps from specifications. The core design decision is to treat roadmap generation as a structured, multi-step pipeline with file-on-disk artifacts between steps — rather than a single large prompt — because each artifact acts as both a quality gate input and a resume checkpoint.

**Why this design exists**: A single monolithic roadmap generation prompt has no way to enforce intermediate quality requirements, provides no recovery surface if one step fails, and cannot systematically exploit model diversity (e.g., architect persona vs. analyzer persona producing different variant roadmaps). The 9-step pipeline with parallel generate steps (2a/2b) was chosen explicitly to produce two independently generated variants that are then compared adversarially, which surfaces assumptions and trade-offs that a single generation would suppress.

**Trade-off**: The pipeline introduces significant latency (up to 900s per generate step, 300s per analysis step) and file I/O overhead compared to a direct prompt. Benefit: each step is independently verifiable; HALT diagnostic output identifies exactly which step failed with a human-readable reason.

## 2. Execution Model

The pipeline is built as a declarative list of `Step` objects (and parallel `list[Step]` groups) constructed by `_build_steps(config: RoadmapConfig)` (`src/superclaude/cli/roadmap/executor.py:302`). Execution is delegated to the shared `execute_pipeline()` function (`src/superclaude/cli/pipeline/executor.py:46`), which processes steps sequentially, dispatching parallel groups via `_run_parallel_steps()`.

**9-step sequence**:
1. `extract` — spec decomposition into structured requirements (5-minute timeout)
2. `generate-<agent_a>` + `generate-<agent_b>` — parallel variant generation (15-minute timeout each)
3. `diff` — structural and content diff analysis between variants
4. `debate` — adversarial debate resolving diff points
5. `score` — hybrid quantitative + qualitative scoring; base selection
6. `merge` — selected base + planned improvements from non-base variant
7. `test-strategy` — test plan generation for merged roadmap
8. `spec-fidelity` — verifies merged roadmap covers all spec requirements

Each step produces a named output file and is validated by `gate_passed(output_file, criteria)` (`src/superclaude/cli/pipeline/gates.py:20`). Gate tiers: EXEMPT / LIGHT / STANDARD / STRICT, with STRICT adding semantic checks (pure Python, no subprocess).

**State persistence**: `_save_state(config, results)` writes `.roadmap-state.json` after each step. `--resume` re-enters the pipeline at the first step that has not yet passed its gate, via `_apply_resume()` (`src/superclaude/cli/roadmap/executor.py:1273`).

**Stale spec detection**: `_apply_resume` computes `sha256` of the spec file and compares to `state["spec_hash"]`. If changed, the extract step is forced to re-run even if its gate previously passed (`src/superclaude/cli/roadmap/executor.py:1287`).

## 3. Quality Enforcement

Quality is enforced at two levels:

**Per-step gates**: `GateCriteria` specifies `required_frontmatter_fields`, `min_lines`, and optional `semantic_checks`. EXTRACT_GATE, GENERATE_A_GATE, GENERATE_B_GATE, DEBATE_GATE, SCORE_GATE each have tier-appropriate criteria. STRICT gates add `SemanticCheck` lambdas that run against file content without LLM invocation (`src/superclaude/cli/pipeline/models.py:58`).

**Spec-fidelity gate**: Step 8 (`spec-fidelity`) is gated by SPEC_FIDELITY_GATE and verifies that the merged roadmap references all requirements from the spec file. This step is explicitly noted to NOT be skipped by `--no-validate` — the `--no-validate` flag only skips the post-pipeline validation subsystem, not spec-fidelity itself (`src/superclaude/cli/roadmap/executor.py:827`).

**Trade-off**: Gate checks are fast (pure Python) but structurally shallow. A gate can pass a syntactically valid document that is semantically empty. The spec-fidelity step adds LLM-based semantic coverage verification, but that step itself is gated only structurally. This creates a residual risk: a low-quality but structurally valid spec-fidelity report will pass the gate.

## 4. Error Handling Strategy

Failures produce structured HALT output via `_format_halt_output()` (`src/superclaude/cli/roadmap/executor.py:437`), which lists failed steps (FAIL or TIMEOUT), passed steps, and cancelled (downstream) steps.

**Retry logic**: Each step has `retry_limit=1` (one retry attempt on gate failure) before the pipeline halts. The retry re-executes the same Claude subprocess with the same prompt — it does not modify the prompt.

**Spec-fidelity auto-resume**: If specifically `spec-fidelity` fails and an auto-resume condition is met, the executor can attempt to auto-resume from that step (`src/superclaude/cli/roadmap/executor.py:883`). This is a targeted recovery path for the most common late-stage failure mode.

**Trade-off**: Retry with identical prompt is a weak recovery mechanism — if the model produced substandard output once, it may do so again. No prompt adaptation occurs on retry. The benefit is simplicity and reproducibility.

## 5. Extension Points

- **Agent specs**: `--agents model[:persona]` injects arbitrary Claude model/persona pairs into generate steps. Default: `opus:architect` + `haiku:architect` (`src/superclaude/cli/roadmap/models.py:85`).
- **Depth control**: `--depth quick|standard|deep` alters the debate step's round configuration.
- **Step list extensibility**: `_build_steps` returns a plain Python list; new steps can be appended without executor changes.
- **Output directory**: Configurable via `--output`; all artifact paths are derived from `config.output_dir`.
- **Resume**: `_apply_resume()` and gate checks enable any step to be skipped on re-entry. No step is hard-coded as non-resumable.

## 6. System Qualities

**Maintainability**: The 9-step pipeline is fully explicit and readable in `_build_steps()`. Each step is a simple dataclass with named fields; no implicit control flow. Sprint and roadmap share the same `execute_pipeline()` function, so executor improvements propagate to both consumers.

**Weakness**: Roadmap pipeline is tightly coupled to the specific 9-step sequence. Adding a step requires modifying `_build_steps()` and potentially defining new gate constants. There is no plugin mechanism for step injection at runtime.

**Checkpoint Reliability**: `.roadmap-state.json` persists step pass/fail status per run. `--resume` reads this state and re-checks gate status on disk. Stale spec detection (hash comparison) prevents silently resuming with a changed spec file.

**Weakness**: State file records step IDs as strings. If a step is renamed between runs, resume logic will not recognize the previously-completed step and will re-run it — producing duplicate artifacts.

**Extensibility**: The `AgentSpec` model is open-ended; any model:persona string is accepted. The parallel generate group is structurally a `list[Step]`, so additional agents can be added without executor changes.

**Weakness**: Adding more than 2 generate agents increases latency proportionally (timeout per agent) and potentially degrades downstream diff quality as the diff step scales O(n²) in comparison complexity.

**Operational Determinism**: Gate validation is pure Python. Same file content produces same gate pass/fail result. The scoring algorithm (50% quantitative + 50% qualitative) and tiebreaker protocol produce deterministic base selection for a given set of inputs.

**Weakness**: The generate steps invoke Claude LLM subprocesses whose outputs are inherently non-deterministic. Two runs of the same pipeline with the same inputs will produce different variant roadmaps, and potentially different final merged outputs.
