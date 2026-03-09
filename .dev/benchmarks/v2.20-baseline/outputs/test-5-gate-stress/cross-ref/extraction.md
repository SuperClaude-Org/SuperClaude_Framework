

---
spec_source: "spec-roadmap-validate.md"
generated: "2026-03-08T00:00:00Z"
generator: "superclaude-extraction-agent"
functional_requirements: 14
nonfunctional_requirements: 7
total_requirements: 21
complexity_score: 0.65
complexity_class: moderate
domains_detected: 4
risks_identified: 6
dependencies_identified: 8
success_criteria_count: 9
extraction_mode: full
---

## Functional Requirements

**FR-001** (FR-050.1): Implement `superclaude roadmap validate <output-dir>` subcommand that accepts a path to a directory containing roadmap pipeline outputs and validates presence of all 3 required files (`roadmap.md`, `test-strategy.md`, `extraction.md`) before running the validation pipeline.

**FR-002** (FR-050.1): Support CLI options `--agents`, `--model`, `--max-turns`, and `--debug` on the `validate` subcommand with defaults of `opus:architect`, empty string, 50, and false respectively.

**FR-003** (FR-050.2): In single-agent mode (default or 1 agent specified), run a single sequential reflection subprocess that produces `<output-dir>/validate/validation-report.md`.

**FR-004** (FR-050.3): In multi-agent mode (2+ agents via `--agents`), run parallel reflection subprocesses per agent producing `reflect-<agent-id>.md` files, followed by a sequential adversarial merge step producing the final `validation-report.md`.

**FR-005** (FR-050.4): Auto-invoke `execute_validate()` from `execute_roadmap()` after the 8-step pipeline succeeds, inheriting `--agents`, `--model`, `--max-turns`, and `--debug` from the parent invocation.

**FR-006** (FR-050.4): Support `--no-validate` flag on `roadmap run` to skip the automatic post-pipeline validation step.

**FR-007** (FR-050.4): When `--resume` is used and all gates pass on existing artifacts, validation still runs on the final artifacts. If the pipeline halts on a failed step, validation is skipped.

**FR-008** (FR-050.5): Validate across 7 dimensions: Schema (BLOCKING), Structure (BLOCKING), Traceability (BLOCKING), Cross-file consistency (BLOCKING), Interleave ratio (WARNING), Decomposition (WARNING), and Parseability (BLOCKING).

**FR-009** (FR-050.6): Produce a `validation-report.md` with YAML frontmatter containing `blocking_issues_count`, `warnings_count`, `info_count`, `tasklist_ready`, `validation_agents`, and `validation_mode` fields.

**FR-010** (FR-050.6): Structure the report body with Summary, Blocking Issues (B-NNN IDs with Dimension/Location/Detail/Fix), Warnings (W-NNN), Info (I-NNN), and Validation Metadata sections.

**FR-011** (FR-050.6): Set `tasklist_ready: true` only when `blocking_issues_count == 0`.

**FR-012** (FR-050.7): In multi-agent mode, include an Agent Agreement Analysis table in the merged report categorizing findings as BOTH_AGREE, ONLY_A, ONLY_B, or CONFLICT (severity disagreements escalated to higher severity).

**FR-013**: Apply `REFLECT_GATE` criteria to individual reflection outputs: required frontmatter fields (`blocking_issues_count`, `warnings_count`, `tasklist_ready`), min 20 lines, STANDARD enforcement, non-empty frontmatter values semantic check.

**FR-014**: Apply `ADVERSARIAL_MERGE_GATE` criteria to merged output: required frontmatter fields (`blocking_issues_count`, `warnings_count`, `tasklist_ready`, `validation_mode`, `validation_agents`), min 30 lines, STRICT enforcement, non-empty frontmatter + agreement table semantic checks.

## Non-Functional Requirements

**NFR-001** (NFR-050.1): Validation step adds ≤10% wall time to the pipeline, targeting ≤2 minutes for single-agent mode.

**NFR-002** (NFR-050.2): No imports from `validate_*` modules in `pipeline/*` modules — maintains unidirectional dependency (validate → roadmap, not vice versa).

**NFR-003** (NFR-050.3): `validate` subcommand works independently of `roadmap run` as a standalone invocation against any output directory.

**NFR-004** (NFR-050.4): Reuses existing pipeline infrastructure (`execute_pipeline`, `ClaudeProcess`, `gate_passed`) with zero new infrastructure components.

**NFR-005** (NFR-050.5): Single-agent and multi-agent code paths share identical logic, differing only in list length (1 vs N).

**NFR-006**: Blocking issues produce warnings in CLI output but do not cause non-zero exit codes — users may proceed with known issues.

**NFR-007**: Validation subprocess runs with context independence from the generation pipeline to eliminate confirmation bias (separate Claude subprocess, not in-session).

## Complexity Assessment

**complexity_score**: 0.65
**complexity_class**: moderate

**Scoring Rationale**:
- **Domain breadth** (+0.15): Spans CLI, subprocess orchestration, prompt engineering, and structured validation — 4 domains but well-bounded.
- **Code scope** (+0.15): 3 new files, 3 modified files. Clear module boundaries with explicit dependency graph. No schema migrations.
- **Integration complexity** (+0.15): Reuses existing pipeline executor and gate infrastructure. Must integrate with `roadmap run` auto-invocation and `--resume` behavior.
- **Algorithmic complexity** (+0.10): Multi-agent parallel execution with adversarial merge is moderately complex but follows established patterns from the parent pipeline.
- **Risk reduction** (-0.10): No breaking changes, purely additive subcommand, `--no-validate` preserves backward compatibility. Well-specified gate criteria and prompt constraints.
- **Spec maturity** (+0.10): Spec is thorough with resolved open items, explicit implementation order, and validation fixes already applied.

## Architectural Constraints

1. **Unidirectional dependency**: `validate_*` modules may import from `roadmap/gates.py` and `pipeline/*`, but `pipeline/*` must never import from `validate_*` (NFR-050.2).
2. **Infrastructure reuse mandate**: Must reuse `execute_pipeline`, `ClaudeProcess`, and `gate_passed` — no new infrastructure classes or subprocess mechanisms (NFR-050.4).
3. **File placement**: New files must reside in `src/superclaude/cli/roadmap/` alongside existing roadmap modules (`validate_executor.py`, `validate_gates.py`, `validate_prompts.py`).
4. **Agent spec format**: Must use identical `model:persona` format as `roadmap run` for consistency and code reuse.
5. **Output directory structure**: Validation outputs go in `<output-dir>/validate/` subdirectory, not in the parent output directory.
6. **Implementation order**: `models.py` → (`validate_gates.py` ‖ `validate_prompts.py`) → `validate_executor.py` → (`commands.py` ‖ `executor.py`), respecting dependency graph.
7. **Gate enforcement tiers**: REFLECT_GATE uses STANDARD enforcement; ADVERSARIAL_MERGE_GATE uses STRICT enforcement.
8. **Subprocess isolation**: Validation must run as a separate Claude subprocess, not in-session, to prevent confirmation bias from the generation context.

## Risk Inventory

**R-001** (medium): **False positive rate in validation findings**. Claude may flag non-issues as BLOCKING, wasting user investigation time. *Mitigation*: Prompt constraint "false positives waste user time" + adversarial merge deduplication reduces false positives.

**R-002** (medium): **Validation subprocess token cost**. Multi-agent validation with 3 input files could consume significant tokens. *Mitigation*: NFR-001 targets ≤2 min wall time; single-agent default for standalone invocation keeps costs low.

**R-003** (low): **Gate criteria too lenient**. REFLECT_GATE min 20 lines may pass shallow reports. *Mitigation*: Semantic checks for non-empty frontmatter values provide content-level validation beyond line count.

**R-004** (medium): **Adversarial merge quality**. The merge step must correctly deduplicate, categorize, and resolve severity conflicts across agent reports. *Mitigation*: Explicit prompt instructions for BOTH_AGREE/ONLY_A/ONLY_B/CONFLICT categories; STRICT gate enforcement on merged output.

**R-005** (low): **`--resume` interaction edge cases**. Validation runs on final artifacts even with `--resume`, but partially valid artifacts from a resumed pipeline could produce misleading validation results. *Mitigation*: Spec explicitly states validation only runs after all gates pass.

**R-006** (low): **Import path coupling**. Reusing `_frontmatter_values_non_empty` from `roadmap/gates.py` creates a coupling point. *Mitigation*: This is a pure function with no side effects; coupling is acceptable per the unidirectional dependency constraint.

## Dependency Inventory

1. **`src/superclaude/cli/roadmap/commands.py`** — existing CLI group to extend with `validate` subcommand and `--no-validate` flag.
2. **`src/superclaude/cli/roadmap/executor.py`** — existing `execute_roadmap()` to modify for auto-invocation.
3. **`src/superclaude/cli/roadmap/models.py`** — existing models module to extend with `ValidateConfig` dataclass.
4. **`src/superclaude/cli/roadmap/gates.py`** — existing gate infrastructure; import `_frontmatter_values_non_empty` and `GateCriteria`/`SemanticCheck` classes.
5. **`src/superclaude/cli/roadmap/pipeline/executor.py`** — `execute_pipeline` function reused for running validation steps.
6. **`click`** — CLI framework for subcommand and option definitions.
7. **`ClaudeProcess`** — existing subprocess management for running Claude validation agents.
8. **`AgentSpec`** — existing agent specification parsing (model:persona format).

## Success Criteria

1. **SC-001**: `superclaude roadmap validate <dir>` exits successfully and produces `validate/validation-report.md` with valid YAML frontmatter containing all required fields.
2. **SC-002**: Single-agent validation completes in ≤2 minutes wall time.
3. **SC-003**: Multi-agent validation produces per-agent reflection files and a merged report with Agent Agreement Analysis table.
4. **SC-004**: `superclaude roadmap run spec.md` auto-invokes validation after pipeline success (verified by presence of `validate/` directory).
5. **SC-005**: `superclaude roadmap run spec.md --no-validate` does not produce a `validate/` directory.
6. **SC-006**: Known issues (duplicate D-IDs, missing milestone refs, untraced requirements) are detected as BLOCKING in the validation report.
7. **SC-007**: Blocking issues produce CLI warnings but exit code 0.
8. **SC-008**: All 7 unit tests and 4 integration tests from section 10 pass.
9. **SC-009**: No imports from `validate_*` exist in `pipeline/*` modules (verified by grep).

## Open Questions

1. **Default agent count asymmetry**: Standalone `validate` defaults to single-agent (`opus:architect`) while `roadmap run` defaults to dual-agent adversarial (`opus:architect,haiku:architect`). The spec documents this intentionally (section 7.2 note), but should the standalone default match `roadmap run` for consistency? Or is cost efficiency the correct priority for standalone use?

2. **Retry semantics**: Steps have `retry_limit=1`. If a reflection subprocess fails the gate on retry, should the overall validation be marked as failed, or should partial results be surfaced? The spec says "validation-report.md may be incomplete" (section 8.3) but doesn't specify whether other successful agent reports should still be available.

3. **Interleave ratio bounds**: Dimension 5 checks `interleave_ratio in [0.1, 1.0]` but the spec doesn't define how interleave_ratio is calculated. This is left to the reflection prompt's interpretation, which could lead to inconsistent validation across agents.

4. **`.roadmap-state.json` interaction**: The spec states validation state is separate from pipeline state, but doesn't specify whether validation completion/failure is recorded anywhere for `--resume` awareness in subsequent runs.
