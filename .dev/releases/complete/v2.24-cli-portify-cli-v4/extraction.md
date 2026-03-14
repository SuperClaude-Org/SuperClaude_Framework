

---
spec_source: "portify-release-spec.md"
generated: "2026-03-13T00:00:00Z"
generator: "claude-opus-4-6-requirements-extractor"
functional_requirements: 7
nonfunctional_requirements: 11
total_requirements: 18
complexity_score: 0.85
complexity_class: complex
domains_detected: 5
risks_identified: 9
dependencies_identified: 12
success_criteria_count: 14
extraction_mode: full
---

## Functional Requirements

**FR-001**: Config Validation (Step: validate-config) — Pure-programmatic step that validates all CLI inputs before any Claude subprocess is launched. Resolves workflow path to a directory containing `SKILL.md`, derives CLI name (strip `sc-` prefix and `-protocol` suffix, convert to kebab/snake case), validates output directory writability, and checks for name collisions with non-portified CLI modules. Writes `validate-config-result.json` on success. Must complete in <1s with no Claude subprocess.

**FR-002**: Component Discovery (Step: discover-components) — Pure-programmatic step that inventories all components of the target workflow using `Path.rglob()` to find SKILL.md, refs/, rules/, templates/, scripts/, and matching command files. Counts lines per component. Produces a structured markdown inventory table (`component-inventory.md`) with YAML frontmatter (`source_skill`, `component_count`). Must complete in <5s with no Claude subprocess.

**FR-003**: Workflow Analysis (Step: analyze-workflow) — Claude-assisted step that reads all discovered components and produces a complete portification analysis document (`portify-analysis.md`). Extracts behavioral flow, identifies step boundaries, classifies each step on the programmatic spectrum (pure-programmatic, claude-assisted, hybrid), maps dependencies and parallel groups, extracts gate requirements, and produces a data flow diagram. Consolidates logical steps 2–5. STRICT gate requiring YAML frontmatter (`source_skill`, `step_count`, `parallel_groups`, `gate_count`, `complexity`) and semantic checks (required analysis sections, data flow diagram). Output under 400 lines.

**FR-004**: Pipeline Design (Step: design-pipeline) — Claude-assisted step that converts workflow analysis into a concrete, code-ready pipeline specification (`portify-spec.md`). Designs the Step graph, defines domain models, writes prompt builder specifications, defines gate criteria with semantic checks, implements pure-programmatic steps as runnable Python code, designs the executor loop, and plans Click CLI integration. STRICT gate with frontmatter (`step_mapping_count`, `model_count`, `gate_definition_count`) and semantic checks. User review gate after this step; `--dry-run` halts pipeline here. Consolidates logical step 6.

**FR-005**: Spec Synthesis (Step: synthesize-spec) — Claude-assisted step that instantiates the release spec template (9KB inline) and populates all sections from Phase 1 and Phase 2 outputs (referenced by `@path`). Includes step consolidation mapping table. Runs SC-003 self-validation to verify zero remaining `{{SC_PLACEHOLDER:*}}` sentinels. STRICT gate. On gate failure, retry prompt includes specific remaining placeholder names for targeted fix. Consolidates logical steps 7–8.

**FR-006**: Brainstorm Gap Analysis (Step: brainstorm-gaps) — Claude-assisted step that invokes existing `/sc:brainstorm` skill (not reimplemented behavioral patterns) against the draft release spec with `--strategy systematic --depth deep --no-codebase`. Post-processing formats findings as structured objects (`{gap_id, description, severity, affected_section, persona}`), incorporates actionable findings into spec body sections marked `[INCORPORATED]`, routes unresolvable items to Section 11 marked `[OPEN]`, and appends Section 12 with summary. STANDARD gate with structural validation (findings table or zero-gap summary text). Pre-flight check verifies `/sc:brainstorm` availability; falls back to inline multi-persona prompt with warning if unavailable. Zero-gap outcome is valid and does not block pipeline. Consolidates logical step 9.

**FR-007**: Panel Review with Convergence (Step: panel-review) — Claude-assisted step with executor-managed convergence loop. Each iteration launches a Claude subprocess invoking existing `/sc:spec-panel` skill with `--focus correctness,architecture`. Executor checks convergence predicate after each iteration: zero unaddressed CRITICALs → CONVERGED; otherwise iterates up to `max_convergence` (default 3). Produces quality scores (clarity, completeness, testability, consistency, overall) and `panel-report.md` with machine-readable convergence block (`CONVERGENCE_STATUS`, `UNADDRESSED_CRITICALS`, `QUALITY_OVERALL`). Overall = mean of 4 dimensions (SC-010). Downstream readiness gate: `overall >= 7.0` (SC-012, boundary: 7.0 true, 6.9 false). STRICT gate. Each iteration runs both focus pass (discussion mode) and critique pass (critique mode) within a single subprocess. Each convergence iteration has its own independent timeout (default 300s). TurnLedger guards budget before each iteration launch. Pre-flight check for `/sc:spec-panel` availability with inline fallback. Terminal states: CONVERGED (success) or ESCALATED (partial, with user escalation). User review gate at end. Consolidates logical steps 10–11.

## Non-Functional Requirements

**NFR-001**: Phase 3 wall clock time < 10 minutes. Measured via `phase_timing.phase_3_seconds`; advisory warning if exceeded.

**NFR-002**: Phase 4 wall clock time < 15 minutes. Measured via `phase_timing.phase_4_seconds`; advisory warning if exceeded.

**NFR-003**: Synchronous execution only — no `async/await`. Verified by code review: zero `async def` or `await` in `cli_portify/`.

**NFR-004**: All gate function signatures return `tuple[bool, str]`. Verified by type checking and unit tests.

**NFR-005**: Runner-authored truth — reports derived from observed data only (exit codes, artifacts, gates). No Claude self-reporting in status determination.

**NFR-006**: Deterministic flow control — Python controls all sequencing. No step uses Claude to decide "what's next."

**NFR-007**: Zero changes to `pipeline/` or `sprint/` base modules. Verified by `git diff`.

**NFR-008**: Additive-only spec modifications — panel review never rewrites existing content. Append/extend only in Steps 4b, 4d. Section hashing enforces this in panel_review.py.

**NFR-009**: All contract fields populated with defaults on failure paths. Verified by unit tests for each failure type.

**NFR-010**: Skill reuse — brainstorm-gaps invokes `/sc:brainstorm`; panel-review invokes `/sc:spec-panel`. Verified by prompt content inspection and integration tests.

**NFR-011**: User review gates — when not `--skip-review`, executor pauses TUI and prompts on stderr; user enters `y` to continue or `n` to halt with `USER_REJECTED` status.

## Complexity Assessment

**Complexity Score**: 0.85 (complex)

**Scoring Rationale**:
- **Multi-phase orchestration** (7 pipeline steps, 4 logical phases): +0.20 — requires careful sequencing, gate validation, and state management across steps
- **Claude subprocess management**: +0.15 — 5 of 7 steps launch Claude subprocesses with prompt builders, output parsing, and timeout handling
- **Convergence loop**: +0.15 — panel-review step implements an executor-managed iteration loop with predicate checking, budget guards, and escalation logic
- **Skill reuse integration**: +0.10 — subprocess invocation of `/sc:brainstorm` and `/sc:spec-panel` with pre-flight checks and fallback paths
- **Resume/checkpoint support**: +0.10 — per-step resumability classification, prior-context injection, partial-artifact preservation
- **Rich TUI + monitoring**: +0.08 — unified monitoring with JSONL logging, markdown reports, signal types, diagnostic collection, and failure classification
- **Return contract emission**: +0.07 — comprehensive contract on all exit paths (success, partial, failed, dry_run) with phase mapping and resume commands

The system extends an existing pipeline/sprint architecture (PipelineConfig, Step, StepResult, GateCriteria, ClaudeProcess, TurnLedger) rather than building from scratch, which bounds complexity. However, the convergence loop, multi-subprocess orchestration, and gate enforcement across 7 steps with 8 semantic check functions place this firmly in the "complex" class.

## Architectural Constraints

1. **Synchronous threading model**: Must use `threading` + `time.sleep()` polling. No `async/await` or `multiprocessing`. Consistent with existing sprint/pipeline architecture.

2. **Extend existing base types**: `PortifyConfig` extends `PipelineConfig`; `PortifyStepResult` extends `StepResult`; `PortifyProcess` extends `pipeline.ClaudeProcess`. Must reuse `GateCriteria`, `GateMode`, `TurnLedger`, `SignalHandler` from pipeline/sprint modules.

3. **Zero modifications to pipeline/ or sprint/ modules**: All changes are additive under `cli_portify/`.

4. **File passing via `@path` references**: Claude subprocesses read files via `@path` in prompts, matching the sprint `ClaudeProcess` pattern. `PortifyProcess` passes `--add-dir` for work directory and workflow path.

5. **Package structure**: 18 modules under `src/superclaude/cli/cli_portify/` with `steps/` subdirectory for step implementations. Single modified file: `main.py`.

6. **Click CLI integration**: Command group registered via `app.add_command(cli_portify_group)` in `main.py`.

7. **Python ≥3.10**: Uses dataclasses, `Path`, type unions (`int | None`), and modern Python features.

8. **UV-only execution**: All Python operations must use `uv run`.

9. **Gate enforcement tiers**: EXEMPT (no validation), STANDARD (basic checks), STRICT (full semantic validation). Gate functions return `tuple[bool, str]`.

10. **Runner-authored truth**: All status determination from observed data (exit codes, file existence, gate results), never from Claude self-reporting.

## Risk Inventory

1. **[HIGH] Large context windows may cause Claude output truncation** (Steps 5–7) — Mitigation: Use `@path` references instead of inline embedding; set generous `max_turns`.

2. **[HIGH] Panel review convergence prompt mode mapping incorrect** (GAP-006) — Each iteration must run both focus (discussion) AND critique within a single subprocess, not mode-per-iteration. Mitigation: Acceptance criterion added to FR-007; prompt design adjusted.

3. **[MEDIUM] Convergence loop may exhaust budget before 3 iterations** — Mitigation: TurnLedger pre-launch guards; budget estimation per iteration; ESCALATED terminal state.

4. **[MEDIUM] `/sc:brainstorm` and `/sc:spec-panel` may not produce machine-readable convergence markers** — Mitigation: Post-processing in executor parses output; fallback to structural checks if markers missing.

5. **[MEDIUM] Subprocess cannot read `@path` files outside working directory scope** (GAP-002) — Mitigation: PortifyProcess passes `--add-dir` for work directory and workflow path via `extra_args`.

6. **[MEDIUM] User review gates have no programmatic interaction mechanism** (GAP-003) — Mitigation: `--skip-review` flag bypasses; otherwise executor pauses TUI and prompts on stderr.

7. **[MEDIUM] Resume from Phase 3: partial synthesize-spec output may not pass gate** (GAP-005) — Mitigation: Define resume entry points precisely during implementation.

8. **[HIGH] Sequential execution results in long wall-clock time** — 7 steps with data dependencies prevent parallelism. Mitigation: Consolidation from 12 to 7 steps reduces overhead; timing is advisory not blocking.

9. **[LOW] Self-portification circularity** — Changes to cli-portify code could affect the workflow being portified. Mitigation: Source skill files are read-only during portification; generated code in separate directory.

## Dependency Inventory

1. **pipeline.models** (`src/superclaude/cli/pipeline/models.py`) — Base types: PipelineConfig, Step, StepResult, GateCriteria, GateMode
2. **pipeline.gates** (`src/superclaude/cli/pipeline/gates.py`) — `gate_passed()` validation engine
3. **pipeline.process** (`src/superclaude/cli/pipeline/process.py`) — Base ClaudeProcess with `extra_args` support
4. **sprint.models** (`src/superclaude/cli/sprint/models.py`) — TurnLedger, GateDisplayState
5. **sprint.process** (`src/superclaude/cli/sprint/process.py`) — Sprint ClaudeProcess pattern, SignalHandler
6. **`/sc:brainstorm` skill** — Multi-persona gap analysis (invoked in subprocess)
7. **`/sc:spec-panel` skill** — Expert panel review with quality scoring (invoked in subprocess)
8. **`claude` binary** — Required in PATH for subprocess execution
9. **Click** (≥8.0.0) — CLI framework for command group and option parsing
10. **Rich** (≥13.0.0) — TUI live dashboard rendering
11. **PyYAML** — YAML parsing for frontmatter and contract emission
12. **release-spec-template.md** (`src/superclaude/examples/release-spec-template.md`) — 9KB template for spec synthesis

## Success Criteria

1. **Config validation completes in <1s** with correct error codes for invalid path, derivation failure, non-writable output, and name collision scenarios.

2. **Component discovery completes in <5s** producing `component-inventory.md` with accurate line counts and YAML frontmatter.

3. **Workflow analysis produces `portify-analysis.md`** passing STRICT gate: all 5 required sections present, data flow diagram with arrow notation, YAML frontmatter with 5 required fields.

4. **Pipeline design produces `portify-spec.md`** passing STRICT gate: step mappings present, 3 required frontmatter fields populated.

5. **Spec synthesis produces zero remaining `{{SC_PLACEHOLDER:*}}` sentinels** (SC-003). Contains 7 functional requirements with explicit consolidation mapping.

6. **Brainstorm gap analysis appends Section 12** with either structured findings table (with Gap ID column) or zero-gap summary text. Gate validates structural content, not just heading presence.

7. **Panel review convergence terminates** with either CONVERGED (0 unaddressed CRITICALs) or ESCALATED (max iterations reached) within 3 iterations.

8. **Quality scores**: overall = mean(clarity, completeness, testability, consistency) within 0.01 tolerance (SC-010).

9. **Downstream readiness**: `overall >= 7.0` → `downstream_ready: true`; `6.9` → false (SC-012 boundary test).

10. **Return contract emitted on all exit paths** (success, partial, failed, dry_run) with all fields populated including defaults on failure (NFR-009).

11. **`--dry-run` halts after design-pipeline** (Step 4), emitting `dry_run` contract with phases 3–4 marked `skipped`.

12. **Zero `async def` or `await`** in any file under `cli_portify/` (NFR-003).

13. **Zero changes to `pipeline/` or `sprint/` modules** verified by `git diff` (NFR-007).

14. **Resume command generated** for resumable failures (brainstorm-gaps, panel-review) with correct `--start` step and suggested budget.

## Open Questions

1. **GAP-004**: Overall score rounding tolerance (`< 0.01`) vs display precision — should scores be displayed to 1 or 2 decimal places? Does rounding affect the `>= 7.0` downstream gate at boundary values (e.g., mean of 7.0025 displays as 7.0)?

2. **GAP-005**: Resume from Phase 3 failure — if `synthesize-spec` partially wrote the spec file, does the gate pass on resume? Should resume re-run `synthesize-spec` or only `brainstorm-gaps`? Need to define per-step resume entry points precisely.

3. **GAP-007**: `to_contract()` uses inline imports (`hashlib`, `yaml`) instead of module-level — should these be moved to module-level imports in `contract.py` during implementation?

4. **GAP-008**: NDJSON signal vocabulary for `monitor.py` — what domain-specific signals does the monitor extract from Claude subprocess output? Need to define the signal types (e.g., persona activation, section completion, placeholder resolution) and their machine-readable patterns.

5. **GAP-009**: `run_discover_components` reads full file content to count lines — acceptable for typical skill directories (<20 files), but should there be a file size cap to prevent memory issues with unexpectedly large files? The spec mentions a 1MB cap with warning but this isn't reflected in the reference implementation.

6. **F-004**: Per-iteration timeout semantics — the spec states each convergence iteration should have its own independent timeout (default 300s), but the reference pseudocode divides total timeout by `max_convergence`. Which is authoritative?

7. **F-006**: Resume from Phase 4 — the spec states prior `focus-findings.md` is preserved as context injection into the first iteration's prompt, but convergence counter resets to 1. How is this context injection implemented? Is `focus-findings.md` a separate artifact or part of `panel-report.md`?

8. **Implementation order discrepancy**: Section 4.6 references files (`config.py`, `inventory.py`, `tui.py`, `logging_.py`, `diagnostics.py`, `commands.py`) that don't appear in the Section 4.1 file table (which uses `steps/` subdirectory and consolidated `monitor.py`, `cli.py`). The DEV-001 deviation note explains the 18-module structure replaced the original 13-file layout, but Section 4.6 was not updated to match. Which is authoritative?

9. **Template availability**: The spec references `src/superclaude/examples/release-spec-template.md` (9KB) but does not include its content or verify its existence. Does this file exist in the repository? What happens if it's missing at runtime?

10. **Subprocess environment**: When `/sc:brainstorm` or `/sc:spec-panel` are invoked in Claude subprocesses, do they have access to MCP servers (Auggie, Sequential, Context7)? The `--no-codebase` flag on brainstorm suggests MCP awareness, but subprocess MCP availability is not specified.
