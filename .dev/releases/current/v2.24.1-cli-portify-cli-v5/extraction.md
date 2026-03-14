

---
spec_source: "portify-release-spec.md"
generated: "2026-03-13T00:00:00Z"
generator: "claude-opus-4-6-requirements-extractor"
functional_requirements: 18
nonfunctional_requirements: 5
total_requirements: 23
complexity_score: 0.65
complexity_class: moderate
domains_detected: 4
risks_identified: 6
dependencies_identified: 8
success_criteria_count: 12
extraction_mode: full
---

## Functional Requirements

**FR-001** — Accept 6 input forms for target resolution: bare command name (`roadmap`), prefixed name (`sc:roadmap`), command file path, skill directory path, skill directory name, and SKILL.md path. All must resolve to a normalized `ResolvedTarget` containing command path, skill directory, and project root.

**FR-002** — Strip `sc:` prefix from prefixed command names before resolution. Return `ERR_TARGET_NOT_FOUND` if the resulting name is empty (input was exactly `"sc:"`).

**FR-003** — Return `ERR_TARGET_NOT_FOUND` with descriptive message when target is empty, whitespace-only, or `None`.

**FR-004** — Return `ERR_AMBIGUOUS_TARGET` when multiple matches exist within the same input type class (e.g., two files in `commands/` matching a bare name). Command-first policy: a bare name matching both a command and a skill resolves as command.

**FR-005** — Resolve command → skill link by parsing the command file's `## Activation` section for the skill reference pattern `Skill sc:<name>-protocol`. Return `ERR_BROKEN_ACTIVATION` if the referenced skill directory does not exist.

**FR-006** — Backward-resolve skill → command by stripping `sc-` prefix and `-protocol` suffix from skill directory name, then searching `commands_dir` for `<name>.md`. Missing command is a warning, not an error.

**FR-007** — Build a hierarchical `ComponentTree` containing Tier 0 (CommandEntry), Tier 1 (SkillEntry with refs/rules/templates/scripts), and agents (AgentEntry). The tree must track `component_count`, `total_lines`, and `all_source_dirs`.

**FR-008** — Extract agent references from SKILL.md using 6 defined regex patterns covering backtick-agent notation, YAML arrays, spawn/delegate/invoke verbs, `uses` references, model-parenthetical patterns, and `agents/` path patterns.

**FR-009** — Support `--include-agent` CLI option to manually inject agents not auto-discovered. Deduplicate against auto-discovered agents by name, with manual entries taking precedence (`referenced_in="cli-override"`). Silently ignore empty string values.

**FR-010** — Record missing agents (referenced but file not found) with `found=False` and emit warnings. Missing agents must not cause pipeline failure.

**FR-011** — Provide `to_flat_inventory()` method on `ComponentTree` for backward-compatible conversion to existing `ComponentInventory` format.

**FR-012** — Provide `to_manifest_markdown()` method on `ComponentTree` producing human-readable Markdown. Support `--save-manifest` CLI option to write this artifact after Step 2.

**FR-013** — Extend `PortifyProcess` to accept `additional_dirs` parameter. Build `--add-dir` args from `ComponentTree.all_source_dirs` with deduplication.

**FR-014** — Implement directory cap: warn when `all_source_dirs` exceeds 10 directories, consolidate to parent directories using `os.path.commonpath()`, and fall back to top 10 by component count. Record consolidation decisions in `resolution_log`.

**FR-015** — Add CLI options `--commands-dir`, `--skills-dir`, `--agents-dir` to override auto-detection of project directories.

**FR-016** — Add validation checks 5-6: command→skill link validity and referenced agent existence. Add error codes `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`. Extend `ValidateConfigResult` with `command_path`, `skill_dir`, `target_type`, `agent_count`, and `warnings` fields, including in `to_dict()`.

**FR-017** — Enrich `component-inventory.md` artifact with Command section (Tier 0 metadata), Agents section (Tier 2 agent table), Cross-Tier Data Flow section, Resolution Log section, and extended frontmatter (`source_command`, `agent_count`, `has_command`, `has_skill`).

**FR-018** — Handle edge cases: standalone commands (no skill) produce `ComponentTree` with `skill=None`, skipping R3/R4; standalone skills (no command) produce `command=None`; multi-skill commands extract only the primary skill from `## Activation` with secondary references logged as warnings.

## Non-Functional Requirements

**NFR-001** — Target resolution must complete in <1 second for all 6 input forms, measured via `time.monotonic()` in `resolve_target()`.

**NFR-002** — Zero modifications to `pipeline/` or `sprint/` base modules. Verifiable via `git diff --name-only`.

**NFR-003** — All new code must be synchronous only — no `async def` or `await` statements. Verifiable via `grep -r "async def|await"`.

**NFR-004** — Full backward compatibility: all existing skill-directory inputs must produce identical behavior. Existing test suite must pass unchanged.

**NFR-005** — Subprocess directory cap at 10 `--add-dir` entries with consolidation warning and logic when exceeded.

## Complexity Assessment

**Score**: 0.65 — **Class**: moderate

**Rationale**: The spec introduces one new module (`resolution.py`, ~350-450 lines) and modifies 6 existing modules with additive, backward-compatible changes. The resolution algorithm is deterministic and pure-Python (no subprocess or async complexity). The primary complexity drivers are: (1) supporting 6 input forms with correct disambiguation, (2) regex-based agent extraction with deduplication, and (3) maintaining full backward compatibility with existing skill-directory workflows. The scope is bounded — no recursive agent resolution, no manifest loading, no changes to pipeline/sprint base modules. Estimated at 19-28 hours across 2-3 sessions, consistent with moderate complexity.

## Architectural Constraints

1. **No new pipeline steps**: Resolution runs within existing Step 1 (validate-config). Step numbering is unchanged.
2. **No base module modifications**: `pipeline/` and `sprint/` modules must not be modified.
3. **Synchronous execution only**: No `async def` or `await` in any new code.
4. **Type convention**: New dataclasses use `Path` objects; existing `ComponentEntry.path` remains `str` for backward compatibility. `to_flat_inventory()` converts `Path` → `str` at the boundary.
5. **Command-first resolution policy**: Bare names matching both a command and a skill always resolve as `COMMAND_NAME`.
6. **O(1)-depth agent discovery**: Only SKILL.md is scanned for agent references. No recursive agent-to-agent resolution.
7. **Existing `resolve_workflow_path()` preserved unchanged**: New resolution is additive alongside the existing method.
8. **Implementation order**: models.py → resolution.py (parallel) → discover_components.py + process.py (parallel) → cli.py + config.py → tests.

## Risk Inventory

1. **Agent extraction regex misses references** — Severity: medium. The 6 regex patterns cover known formats but may miss novel reference styles. Mitigation: `--include-agent` escape hatch; iterate patterns based on real-world testing.

2. **Backward-compatible resolution breaks existing workflows** — Severity: high (probability: low). Changing CLI argument from `WORKFLOW_PATH` to `TARGET` could alter behavior. Mitigation: extensive test coverage with existing fixtures; `resolve_workflow_path()` preserved unchanged; skill-directory inputs route through backward-resolution path.

3. **`--add-dir` with many directories causes subprocess issues** — Severity: medium (probability: low). Excessive directories could hit argument length limits or over-scope subprocess access. Mitigation: cap at 10 directories with consolidation logic.

4. **YAML frontmatter parsing failures** — Severity: low (probability: low). Malformed frontmatter in command/skill files. Mitigation: graceful degradation — if frontmatter fails, discover by convention.

5. **Project root detection fails in non-standard layouts** — Severity: low (probability: medium). Auto-detection relies on `src/superclaude/` or `pyproject.toml`. Mitigation: explicit `--commands-dir`, `--skills-dir`, `--agents-dir` overrides with error message suggesting these flags.

6. **Reverse-resolution (skill → command) fragile with non-standard naming** — Severity: low (probability: medium). Stripping `sc-` and `-protocol` is heuristic. Mitigation: missing command is a warning, not error; pipeline continues with `command=None`.

## Dependency Inventory

1. **`models.py` — `ComponentEntry`, `ComponentInventory`, `PipelineConfig`**: Existing data models extended with new dataclasses.
2. **`discover_components.py`**: Existing discovery logic refactored to support `ComponentTree` with backward-compatible wrapper.
3. **`process.py` — `ClaudeProcess`**: Parent class for `PortifyProcess`; extended with `additional_dirs` parameter.
4. **`validate_config.py`**: Existing validation extended with new checks and error codes.
5. **`cli.py` — Click framework**: CLI argument and option definitions changed; depends on Click's `@click.argument`, `@click.option`.
6. **`config.py` — `load_portify_config()`**: Config loader extended with new parameter passthrough.
7. **Python `re` module**: Regex-based agent extraction patterns.
8. **Python `os.path.commonpath()`**: Directory consolidation for subprocess scoping cap.

## Success Criteria

1. `resolve_target("roadmap")` resolves to correct command + skill + agents within <1s.
2. `resolve_target("sc:roadmap")` strips prefix and resolves identically to bare name.
3. `resolve_target("src/.../sc-roadmap-protocol/")` backward-resolves the command file.
4. `resolve_target("nonexistent")` returns `ERR_TARGET_NOT_FOUND` with descriptive message.
5. `ComponentTree` contains correct `CommandEntry`, `SkillEntry`, and `AgentEntry` instances for a standard workflow.
6. Agent extraction finds references matching all 6 regex patterns in test SKILL.md.
7. `--include-agent` adds manually specified agents; deduplicates against auto-discovered.
8. Missing agents recorded with `found=False`, emitted as warnings, pipeline continues.
9. `to_flat_inventory()` produces output identical to existing `ComponentInventory` for same inputs.
10. All existing tests pass unchanged (backward compatibility).
11. `PortifyProcess` with `additional_dirs=None` preserves exact v2.24 behavior.
12. ~37 new tests pass covering all resolution paths, edge cases, and integration scenarios.

## Open Questions

1. **OI-1: Recursive agent-to-agent resolution** — Should agents that delegate to sub-agents have their references recursively resolved? Currently deferred to v2.25 with O(1)-depth in v2.24.1. Could cause incomplete component trees for deeply nested agent workflows.

2. **OI-2: Manifest loading as input** — Should `--manifest` (load) be supported alongside `--save-manifest` (write)? Currently deferred to v2.25. Would enable pre-computed component trees as pipeline input.

3. **OI-3: `--exclude-component` support** — Should users be able to exclude specific components from the resolved tree? Deferred to v2.25; not needed if discovery is accurate.

4. **Multi-skill command handling** — When a command references multiple skills via `## Activation`, only the primary is resolved. Secondary skill references are logged as warnings. Should secondary skills be automatically included? What determines "primary" if multiple `Skill` directives exist?

5. **Diamond agent references** — When the same agent is referenced from multiple sources, the first source is recorded in `referenced_in`. Should all sources be tracked (e.g., as a list) for traceability?

6. **`--add-dir` consolidation threshold** — The 3x file count rule for parent directory substitution is somewhat arbitrary. Should this be configurable or based on empirical data?
