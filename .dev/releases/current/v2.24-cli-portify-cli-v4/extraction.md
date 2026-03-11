

---
spec_source: portify-release-spec.md
generated: "2026-03-10T00:00:00Z"
generator: requirements-extraction-agent
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

- **FR-001** (FR-PORTIFY-CLI.1): **Config Validation** — Pure-programmatic step that validates all CLI inputs before any Claude subprocess is launched. Must resolve `--workflow` to a directory containing `SKILL.md`, derive CLI name (strip `sc-` prefix and `-protocol` suffix, convert to kebab/snake case), validate output directory writability, and detect name collisions with existing non-portified modules. Writes `validate-config-result.json` on success. Must complete in <1s with no Claude subprocess.

- **FR-002** (FR-PORTIFY-CLI.2): **Component Discovery** — Pure-programmatic step that inventories all components of the target workflow using `Path.rglob()`. Finds SKILL.md, refs/, rules/, templates/, scripts/, and matching command files. Counts lines per component. Produces `component-inventory.md` with YAML frontmatter (`source_skill`, `component_count`). Must complete in <5s with no Claude subprocess. Depends on FR-001.

- **FR-003** (FR-PORTIFY-CLI.3): **Workflow Analysis** — Claude-assisted step that reads all discovered components and produces `portify-analysis.md`. Extracts behavioral flow, identifies step boundaries, classifies each step on programmatic spectrum (pure-programmatic, claude-assisted, hybrid), maps dependencies and parallel groups, extracts gate requirements, produces data flow diagram. Output must contain all required sections (Source Components, Step Graph, Gates Summary, Data Flow Diagram, Classification Summary). STRICT gate validation. Under 400 lines. Depends on FR-002.

- **FR-004** (FR-PORTIFY-CLI.4): **Pipeline Design** — Claude-assisted step that converts workflow analysis into code-ready pipeline specification `portify-spec.md`. Designs Step graph, defines domain models, writes prompt builder specifications, defines gate criteria with semantic checks, implements pure-programmatic steps as runnable Python, designs executor loop, plans Click CLI integration. Must use synchronous threading (not async/await). STRICT gate validation. User review gate after this step; `--dry-run` halts here. Depends on FR-003.

- **FR-005** (FR-PORTIFY-CLI.5): **Spec Synthesis** — Claude-assisted step that instantiates the release spec template (9KB inline) and populates all sections from Phase 1 and 2 outputs (referenced by `@path`). Must produce `portify-release-spec.md` with complete YAML frontmatter, zero remaining `{{SC_PLACEHOLDER:*}}` sentinels (SC-003), 7 functional requirements (one per pipeline step), explicit FR consolidation mapping. On gate failure, retry prompt includes specific remaining placeholder names. STRICT gate validation. Depends on FR-004.

- **FR-006** (FR-PORTIFY-CLI.6): **Brainstorm Gap Analysis** — Claude-assisted step that invokes existing `/sc:brainstorm` skill (not reimplemented patterns) against draft release spec. Post-processes findings into structured format `{gap_id, description, severity, affected_section, persona}`. Incorporates actionable findings into spec body sections marked `[INCORPORATED]`, routes unresolvable items to Section 11 marked `[OPEN]`. Appends Section 12 with summary. Zero-gap outcome is valid. Pre-flight check for skill availability with inline fallback. Section 12 gate requires findings table or zero-gap summary text, not just heading. STANDARD gate validation. Depends on FR-005.

- **FR-007** (FR-PORTIFY-CLI.7): **Panel Review with Convergence** — Claude-assisted step with executor-managed convergence loop. Each iteration invokes existing `/sc:spec-panel` skill (not reimplemented expert patterns) with `--focus correctness,architecture`. Python executor checks convergence predicate: zero unaddressed CRITICALs → CONVERGED; otherwise iterates up to `max_convergence` (default 3). Produces quality scores (clarity, completeness, testability, consistency, overall where overall = mean of 4 dimensions per SC-010). Machine-readable convergence block in `panel-report.md`. Downstream readiness gate: `overall >= 7.0` (boundary: 7.0 true, 6.9 false per SC-012). Each iteration runs both focus (discussion) and critique within a single subprocess per GAP-006. Each iteration has independent timeout (default 300s) with TurnLedger budget guard per F-004. Pre-flight skill availability check. STRICT gate validation. User review gate at end. Depends on FR-006.

## Non-Functional Requirements

- **NFR-001**: Phase 3 wall clock time < 10 minutes. Measured via `phase_timing.phase_3_seconds`. Advisory warning if exceeded; non-blocking.

- **NFR-002**: Phase 4 wall clock time < 15 minutes. Measured via `phase_timing.phase_4_seconds`. Advisory warning if exceeded; non-blocking.

- **NFR-003**: Synchronous execution only — zero `async def` or `await` keywords anywhere in `cli_portify/`. Threading + `time.sleep()` polling model. Verified by code review.

- **NFR-004**: All gate functions return `tuple[bool, str]` signature. Verified by type checking and unit tests.

- **NFR-005**: Runner-authored truth — all reports derived from observed data (exit codes, artifacts, gates), never from Claude self-reporting in status determination.

- **NFR-006**: Deterministic flow control — Python controls all sequencing. No step uses Claude to decide "what's next."

- **NFR-007**: Zero modifications to pipeline/ or sprint/ base modules. Verified by `git diff`.

- **NFR-008**: Additive-only spec modifications — panel review never rewrites existing content, only append/extend operations in Steps 4b and 4d.

- **NFR-009**: Failure path defaults — all contract fields populated on every failure type. Verified by unit tests for each failure path.

- **NFR-010**: Skill reuse — brainstorm-gaps invokes `/sc:brainstorm`; panel-review invokes `/sc:spec-panel`. Verified by prompt content inspection and integration test.

- **NFR-011**: User review gates — when `--skip-review` is not set, executor pauses TUI and prompts on stderr; user enters `y` to continue or `n` to halt with `USER_REJECTED` status.

## Complexity Assessment

**Score**: 0.85 — **Class**: complex

**Rationale**:
- **Multi-phase pipeline** (7 steps across 5 phases) with mixed execution modes (pure-programmatic + Claude-assisted): +0.20
- **Convergence loop management** with executor-controlled iteration, budget guards, and multiple terminal states: +0.15
- **Subprocess orchestration** invoking existing skills (`/sc:brainstorm`, `/sc:spec-panel`) with pre-flight checks and fallback paths: +0.15
- **13 new Python modules** with cross-module dependency graph and integration into existing CLI framework: +0.15
- **Gate system** with 7 gate definitions, 7 semantic check functions, and tier-based enforcement: +0.10
- **Rich TUI monitoring**, JSONL+Markdown dual logging, diagnostics with failure classification: +0.05
- **Resume support** with partial execution state preservation: +0.05
- Mitigation: leverages existing pipeline/sprint primitives, no async complexity, well-defined contracts: -0.00 (already factored into the 0.85 score)

## Architectural Constraints

1. **Synchronous execution model**: Threading + `time.sleep()` polling only. No `async/await` permitted (NFR-003).
2. **Zero modification to base modules**: `pipeline/` and `sprint/` directories must not be changed (NFR-007).
3. **Extends existing primitives**: Must use `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode` from `pipeline.models`; `TurnLedger`, `GateDisplayState` from `sprint.models`; `ClaudeProcess` from `pipeline.process`.
4. **File passing via `@path`**: Subprocess reads files via Claude's Read tool using `@path` references in prompts; no `--file` CLI args or inline embedding for large artifacts.
5. **`--add-dir` for subprocess file access**: `PortifyProcess` must pass `--add-dir` for work directory and workflow path so subprocess can read `@path` referenced files (GAP-002).
6. **Skill reuse over reimplementation**: Brainstorm and panel review steps must invoke existing `/sc:brainstorm` and `/sc:spec-panel` skills, not reimplement their behavioral patterns.
7. **Runner-authored truth**: All status determination from observed data (exit codes, file artifacts, gate results), never Claude self-reporting (NFR-005).
8. **Deterministic flow control**: Python decides all sequencing; Claude subprocesses handle content only (NFR-006).
9. **Click CLI integration**: New `cli-portify` group registered in `main.py` via `app.add_command()`.
10. **Module placement**: All new code under `src/superclaude/cli/cli_portify/` (13 modules).
11. **Gate function signature**: All return `tuple[bool, str]` (NFR-004).
12. **Additive-only modifications**: Panel review steps may only append/extend spec content, never rewrite (NFR-008).

## Risk Inventory

1. **R-001** (High): Large context windows in Steps 5-7 may cause Claude to truncate output. *Mitigation*: Use `@path` references instead of inline embedding; set generous `max_turns`.

2. **R-002** (Medium): Convergence loop may exhaust budget before completing 3 iterations. *Mitigation*: TurnLedger pre-launch guards; budget estimation per iteration; ESCALATED terminal state.

3. **R-003** (Medium-High): `/sc:brainstorm` and `/sc:spec-panel` may not produce machine-readable convergence markers. *Mitigation*: Post-processing in executor parses output; fallback to structural checks if markers missing.

4. **R-004** (High-Likelihood, Low-Impact): Sequential execution results in long wall-clock time. *Mitigation*: Inherent to data flow dependencies; 7 steps vs 12 reduces overhead; timing is advisory not blocking.

5. **R-005** (Low): Self-portification circularity — changes to cli-portify code affect the workflow being portified. *Mitigation*: Source skill files are read-only during portification; generated code in separate directory.

6. **R-006** (Low-Probability, High-Impact): Subprocess skill invocation may fail if commands not installed. *Mitigation*: Pre-flight check verifies `claude` binary; config validation checks skill availability.

7. **R-007** (Medium): Subprocess cannot read `@path` files outside its working directory scope. *Mitigation*: PortifyProcess passes `--add-dir` for work directory and workflow path (GAP-002).

8. **R-008** (Medium): User review gates have no programmatic interaction mechanism. *Mitigation*: `--skip-review` flag bypasses; otherwise executor pauses TUI and prompts on stderr (GAP-003).

9. **R-009** (High): Panel review convergence prompt uses wrong mode mapping across iterations. *Mitigation*: Each iteration runs focus (discussion) then critique within a single subprocess, not mode-per-iteration (GAP-006).

## Dependency Inventory

1. **pipeline.models** — Base types: `PipelineConfig`, `Step`, `StepResult`, `GateCriteria`, `GateMode`
2. **pipeline.gates** — `gate_passed()` validation engine
3. **pipeline.process** — Base `ClaudeProcess` with `extra_args` support
4. **sprint.models** — `TurnLedger`, `GateDisplayState`
5. **sprint.process** — Sprint `ClaudeProcess` pattern, `SignalHandler`
6. **Click** (>=8.0.0) — CLI framework for command group and option parsing
7. **Rich** (>=13.0.0) — TUI live dashboard rendering
8. **PyYAML** — Frontmatter parsing in gate semantic checks and contract emission
9. **`claude` CLI binary** — Required in PATH for subprocess invocation
10. **`/sc:brainstorm` skill** — Invoked by brainstorm-gaps step (with inline fallback if unavailable)
11. **`/sc:spec-panel` skill** — Invoked by panel-review step (with inline fallback if unavailable)
12. **Release spec template** (`src/superclaude/examples/release-spec-template.md`) — 9KB template for synthesize-spec step

## Success Criteria

1. **SC-001**: Pipeline completes end-to-end for at least one non-trivial workflow (e.g., `sc-cleanup-audit`), producing a `portify-release-spec.md` with `downstream_ready: true`.
2. **SC-002**: `--dry-run` mode halts after Phase 2 and emits a valid `dry_run` return contract.
3. **SC-003**: Zero remaining `{{SC_PLACEHOLDER:*}}` sentinels in synthesized spec (gate-enforced).
4. **SC-004**: Convergence loop terminates correctly: CONVERGED when 0 unaddressed CRITICALs, ESCALATED after max iterations.
5. **SC-005**: All 7 gate definitions enforce their specified tier (EXEMPT/STANDARD/STRICT) with semantic checks passing/failing appropriately.
6. **SC-006**: Resume command generated on resumable failures, enabling continuation from the halted step.
7. **SC-007**: Return contract YAML conforms to the Phase Contracts schema (Section 5.3) on all paths: success, partial, failed, dry_run.
8. **SC-008**: Pure-programmatic steps (validate-config, discover-components) complete without Claude subprocess and within time bounds (<1s, <5s respectively).
9. **SC-009**: Zero `async def` or `await` in any file under `cli_portify/` (NFR-003).
10. **SC-010**: Overall quality score = arithmetic mean of clarity, completeness, testability, consistency (tolerance <0.01).
11. **SC-011**: Zero modifications to files under `pipeline/` or `sprint/` directories (NFR-007).
12. **SC-012**: Downstream readiness boundary: `overall >= 7.0` → true, `overall == 6.9` → false.
13. **SC-013**: All 17 unit tests pass (Section 8.1).
14. **SC-014**: All 5 integration tests pass (Section 8.2).

## Open Questions

1. **GAP-004**: Overall score rounding tolerance (`< 0.01`) vs display precision not specified — should scores display to 1 or 2 decimal places? Does rounding occur before or after comparison?

2. **GAP-005**: Resume from Phase 3 failure: if `synthesize-spec` partially wrote the spec file, does the gate pass on resume? Should resume re-run `synthesize-spec` entirely, or only subsequent steps?

3. **GAP-007**: `to_contract()` uses inline imports (`hashlib`, `yaml`) instead of module-level — is this intentional for lazy loading or should they be hoisted?

4. **GAP-008**: No NDJSON signal vocabulary defined for `monitor.py` — what domain-specific signals does the monitor extract from Claude subprocess output? What are the event types and their schemas?

5. **GAP-009**: `run_discover_components` reads full file content to count lines — acceptable for typical skill directories (<20 files), but should there be a file size limit or lazy counting for large files?

6. **F-006**: Resume from Phase 4: the spec mentions that prior `focus-findings.md` should be preserved as context injection into the first iteration's prompt, but the convergence counter should reset to 1. This is noted but not fully specified in the prompt builders.

7. **User review gate UX**: When the executor pauses for user review (NFR-011), what information is displayed? Is the full spec rendered, or just a summary with a path to the file? Is there a timeout for user response?

8. **Template location stability**: The release spec template is referenced at `src/superclaude/examples/release-spec-template.md` — does this path exist and is it stable, or could it move between versions?

9. **Model override scope**: The `--model` CLI option is defined but its propagation to subprocess invocations is not specified — does it apply to all Claude subprocesses or only specific steps?

10. **Convergence predicate ambiguity**: The convergence check parses `panel-report.md` for string literals `"CONVERGENCE_STATUS: CONVERGED"` and `"UNADDRESSED_CRITICALS: 0"` — what happens if `/sc:spec-panel` produces these markers in a different format or location within the file?
