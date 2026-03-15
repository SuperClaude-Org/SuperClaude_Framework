---
component: pipeline-analysis
framework: IronClaude
phase: 3
generated: 2026-03-14
evidence_source: auggie-mcp
oq002: single-group
---

# Strategy: IronClaude Pipeline Analysis Subsystem

## 1. Design Philosophy

The pipeline analysis subsystem exists to provide a generic, reusable execution infrastructure that multiple pipeline consumers (sprint, roadmap, cleanup-audit) share without creating import cycles. The core design principle is **composition via callable injection**: consumers inject their own step runners and callbacks; the executor handles ordering, retry, parallel dispatch, and state management without knowing anything about the consumer domain.

**Why this design exists**: Sprint and roadmap share fundamentally the same execution pattern — iterate over steps, validate gates, retry on failure, halt on exhaustion. Without a shared library, each consumer would have duplicated gate logic, parallel dispatch code, and retry handling. NFR-007 (`src/superclaude/cli/pipeline/executor.py:7`) enforces no imports from `superclaude.cli.sprint` or `superclaude.cli.roadmap` in the pipeline module — this prevents accidental coupling and ensures the executor remains consumer-agnostic.

The analytical sub-passes (FMEA, dataflow, guard, invariant) address a higher-order problem: LLM-assisted pipeline specifications frequently contain implicit contracts between deliverables (e.g., deliverable A writes a state variable that deliverable B reads) that are never made explicit. The analytical passes detect and surface these contracts before they become runtime failures.

**Trade-off**: A 42-symbol public API surface (`src/superclaude/cli/pipeline/__init__.py:3`) is large. Consumers importing from this module receive a comprehensive toolbox, but the API surface also creates a large compatibility boundary — changes to any of the 42 exported symbols are potentially breaking changes for consumers.

## 2. Execution Model

**Core executor**: `execute_pipeline(steps, config, run_step, ...) -> list[StepResult]` (`src/superclaude/cli/pipeline/executor.py:46`). Processes each element in `steps` — either a single `Step` (sequential) or a `list[Step]` (parallel group). For parallel groups: all steps run concurrently via `_run_parallel_steps()`, any failure cancels remaining steps.

**Gate validation**: `gate_passed(output_file, criteria) -> (bool, str | None)` (`src/superclaude/cli/pipeline/gates.py:20`). Pure Python, no subprocess, no LLM. Tier-proportional checks:
- EXEMPT → always passes
- LIGHT → file exists + non-empty
- STANDARD → + min lines + YAML frontmatter fields
- STRICT → + semantic checks (callable lambdas in `GateCriteria.semantic_checks`)

**Trailing gate runner**: `TrailingGateRunner` executes gates asynchronously in a daemon thread with a configurable grace period, enabling shadow gate mode (metrics without blocking). Trailing gate failures are collected at a sync point at the end of the pipeline rather than halting individual steps.

**Analytical passes** (pipeline order: M1 → M2 → M3 → M4):
- **M1 Decomposition**: `decompose_deliverables()` — breaks deliverables into atomic units by kind (IMPLEMENT, INVARIANT_CHECK, GUARD_TEST, etc.)
- **M2 Combined pass**: `run_combined_m2_pass()` — invariant registry + FMEA sub-passes concurrently
  - Invariant registry: `run_invariant_registry_pass()` detects state variables, builds mutation inventory, generates `InvariantEntry` objects with constrained predicates (`src/superclaude/cli/pipeline/invariant_pass.py:39`)
  - FMEA classifier: `classify_failure_modes()` uses dual-signal detection — Signal 1 (invariant cross-reference: violation without error = silent corruption) + Signal 2 (no-error-path detection: degenerate input categories: EMPTY, NULL, ZERO, NEGATIVE, FILTER_ALL) (`src/superclaude/cli/pipeline/fmea_classifier.py:129`)
- **M3 Guard analysis**: `run_guard_analysis_pass()` — detects `if/else` guards, type transitions, cross-references with invariant predicates, checks FMEA severity for elevation to silent corruption (`src/superclaude/cli/pipeline/guard_pass.py:50`)
- **M4 Dataflow tracing**: `run_dataflow_tracing_pass()` — builds cross-deliverable state variable graph (birth/write/read nodes), extracts implicit contracts (`ImplicitContract`), detects conflicts

**Diagnostic chain**: `run_diagnostic_chain()` (`src/superclaude/cli/pipeline/diagnostic_chain.py`) — 4-stage failure diagnostic: troubleshoot → adversarial analysis × 2 → summary. Degrades gracefully: stage errors are isolated and partial results remain available.

## 3. Quality Enforcement

**Pure-Python gate validation**: `gate_passed()` is a pure function with no side effects, no subprocess calls, no LLM invocations. This is enforced by NFR-003 (no subprocess import in gates.py). Same file content + same criteria = same gate result, always.

**FMEA dual-signal detection**: By combining Signal 1 (invariant violations) and Signal 2 (no-error-path for degenerate inputs), the classifier can detect silent corruption risk even when no invariant predicates are registered — Signal 2 operates independently (`src/superclaude/cli/pipeline/fmea_classifier.py:7`).

**Guard annotation suppression**: `@no-ambiguity-check` annotation in deliverable descriptions suppresses guard ambiguity detection (R-009). This allows known guard patterns to be exempted from false-positive warnings while preserving detection for unlabeled guards.

**FMEA promotion**: `promote_failure_modes()` (`src/superclaude/cli/pipeline/fmea_promotion.py`) elevates FMEA failure modes to `ReleaseGateViolation` objects when severity exceeds a threshold. These violations propagate to gate criteria as structured reasons for HALT.

**Trade-off**: The analytical passes operate on deliverable descriptions (text) rather than actual code. This means the FMEA and invariant analysis is based on what deliverables are _described_ to do, not what they actually implement. A deliverable description that omits a state variable or error condition will not be detected by the analysis passes, creating blind spots for poorly-specified deliverables.

## 4. Error Handling Strategy

**Graceful diagnostic degradation**: `run_diagnostic_chain()` isolates errors per stage — a failure in stage 2 does not prevent stage 3 from running. Partial diagnostic results are accumulated and returned even if some stages fail.

**Retry logic**: Each `Step` has a configurable `retry_limit` (typically 1). On gate failure, the step is re-run up to `retry_limit` times before the pipeline halts. Retry executes the same `run_step` callable with the same inputs — no prompt adaptation.

**Cancel check**: `cancel_check: Callable[[], bool]` is polled before each step and between parallel sub-steps. Returning `True` cancels remaining steps gracefully, producing `CANCELLED` status without abrupt termination (`src/superclaude/cli/pipeline/executor.py:88`).

**DFS cycle detection on dataflow graph**: `build_dataflow_graph()` includes depth-first search cycle detection to prevent infinite loops in deliverable dependency resolution.

**Trade-off**: Retry with identical prompt is a limited recovery strategy. If the LLM step failed because the prompt was ambiguous or the model produced systematically low-quality output, retrying with the same prompt will likely produce a similar failure. No prompt modification occurs between retries.

## 5. Extension Points

- `run_step: StepRunner` — injectable callable; consumers provide their domain-specific step execution (`src/superclaude/cli/pipeline/executor.py:49`).
- `cancel_check: Callable[[], bool]` — injectable for graceful cancellation by external signals.
- `trailing_runner: TrailingGateRunner | None` — injectable for shadow gate mode.
- `GateCriteria.semantic_checks: list[SemanticCheck]` — custom content validators addable per step.
- FMEA `Severity` threshold for promotion to `ReleaseGateViolation` — configurable per deployment.
- `@no-ambiguity-check` annotation — per-deliverable suppression of guard ambiguity detection.

## 6. System Qualities

**Maintainability**: NFR-007 enforces no reverse imports (pipeline → sprint/roadmap is forbidden). This ensures `pipeline/` is a genuine library layer with no hidden dependencies on consumers. The 42-symbol public API is explicit and reviewable in `__init__.py`.

**Weakness**: 42 exported symbols is a large API surface for a library module. Not all symbols are consumed by both sprint and roadmap — some (e.g., FMEA analysis passes) are only used by specific consumer workflows. No mechanism exists to mark symbols as intended for specific consumers vs. general use.

**Checkpoint Reliability**: `run_diagnostic_chain()` degrades gracefully per stage — partial results are available even on mid-chain failure. The dataflow graph supports DFS cycle detection. Gate results are pure and deterministic for given inputs.

**Weakness**: The analytical passes (M2–M4) have no intermediate checkpoint mechanism. If `run_combined_m2_pass()` fails midway through the invariant registry sub-pass, the work is lost and the entire M2 pass must restart.

**Extensibility**: `run_step` callable injection makes the executor reusable across pipeline types. `SemanticCheck` lambdas enable per-step content validation without modifying the executor. FMEA threshold configurability enables per-project sensitivity tuning.

**Weakness**: The analytical passes (M2–M4) operate on deliverable descriptions as text. There is no AST or structured representation of deliverable semantics — all analysis relies on natural language parsing patterns (e.g., detecting "if/else" guards via text matching in `guard_analyzer.py`). This makes the analysis brittle to description phrasing variations.

**Operational Determinism**: `gate_passed()` is a pure function — same inputs always produce same output. DFS cycle detection on dataflow graph ensures termination. FMEA dual-signal detection is deterministic for a given set of deliverable descriptions and domain maps.

**Weakness**: The guard analyzer uses textual pattern matching (if/else, type changes) to detect guards. This approach has both false positives (text patterns that match but are not guards) and false negatives (guard logic expressed in non-canonical phrasings). The `@no-ambiguity-check` annotation provides manual correction for false positives but does not address false negatives.
