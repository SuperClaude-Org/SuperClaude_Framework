---
spec_source: "portify-release-spec.md"
complexity_score: 0.65
adversarial: true
---

# v2.24.1 CLI Portify v5 — Final Merged Roadmap

## Executive Summary

This release extends the CLI Portify pipeline with a unified target resolution system, replacing the single skill-directory input with 6 input forms (bare name, prefixed name, command path, skill directory path, skill directory name, SKILL.md path). The core addition is `resolution.py` (~350-450 lines) plus additive modifications to 6 existing modules.

The architecture is constrained to synchronous, backward-compatible changes with zero modifications to `pipeline/` or `sprint/` base modules. The dominant risk is not feature breadth but behavioral regression in existing workflows. Accordingly, this roadmap adopts a compatibility-first incremental delivery with continuous testing gates at every milestone boundary.

**Scope**: 3 functional requirements with 18 acceptance-criteria bullets, 5 non-functional requirements, 4 domains (resolution, discovery, CLI, validation), ~37 new tests.

**Estimated effort**: 19-28 hours across 3 phases (Sessions 1-3).

### Architectural Priorities

1. **Preserve existing workflows first** — Existing skill-directory inputs remain behaviorally identical. `resolve_workflow_path()` is unchanged; the new resolver is additive.
2. **Isolate new logic** — Resolution rules concentrated in a dedicated module. Boundary conversions explicit between new `Path`-based dataclasses and legacy string-based inventory outputs.
3. **Maintain deterministic behavior** — Resolution precedence, ambiguity handling, and warning/error semantics are explicit, testable, and logged.
4. **Control subprocess scope** — 10-directory cap with two-tier deterministic consolidation and auditability via `resolution_log`.

---

## Phase 1: Foundation — Pre-work, Models & Resolution Core

**Goal**: Establish delivery guardrails, data models, and the deterministic resolution algorithm.

**Duration**: 6-10 hours (Session 1)

### Milestone 1.0: Pre-work & Delivery Guardrails

Before code changes begin, produce three lightweight artifacts:

1. **Change map**: Enumerate impacted files — `models.py`, new `resolution.py`, `discover_components.py`, `process.py`, `cli.py`, `config.py`, `validate_config.py`, tests.
2. **Compatibility checklist**: Explicit confirmation of constraints — no `pipeline/`/`sprint/` edits, no async code, existing skill-directory behavior unchanged, `resolve_workflow_path()` untouched.
3. **Test matrix outline**: Catalog existing tests and identify coverage gaps for new resolution paths.

These deliverables formalize the continuous testing contract: **`uv run pytest` must pass at every subsequent milestone boundary. A milestone is not complete until existing tests pass.**

### Milestone 1.1: Data Models (`models.py`)

1. Define `TargetInputType` enum with the 5 spec-defined values: `COMMAND_NAME`, `COMMAND_PATH`, `SKILL_DIR`, `SKILL_NAME`, `SKILL_FILE`
2. Define `ResolvedTarget` dataclass with all spec-required fields: `input_form: str`, `input_type: TargetInputType`, `command_path: Path | None`, `skill_dir: Path | None`, `project_root: Path`, `commands_dir: Path`, `skills_dir: Path`, `agents_dir: Path`
3. Define `CommandEntry` (Tier 0), `SkillEntry` (Tier 1), `AgentEntry` (Tier 2) dataclasses
4. Define `ComponentTree` with `command`, `skill`, `agents` fields plus `component_count`, `total_lines`, `all_source_dirs` computed properties
5. Extend `PortifyConfig` with the spec-required fields: `target_input`, `target_type`, `command_path`, `commands_dir`, `skills_dir`, `agents_dir`, `project_root`, `include_agents`, `save_manifest_path`, `component_tree`
6. Augment `derive_cli_name()` to prefer the resolved command name when available, while retaining backward-compatible fallback behavior
7. Implement `to_flat_inventory()` → backward-compatible `ComponentInventory` conversion (`Path` → `str` at boundary)
8. Implement `to_manifest_markdown()` → human-readable Markdown output
9. Add error code constants: `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`

**Validation gate**: Unit tests for all dataclass construction, `to_flat_inventory()` round-trip, error code values. Existing test suite passes.

### Milestone 1.2: Resolution Algorithm (`resolution.py`)

1. Implement `resolve_target(target: str, ...) → ResolvedTarget` with `time.monotonic()` timing (`FR-PORTIFY-WORKFLOW.1`, `NFR-001`)
2. Implement input classification: detect which of 6 forms the input matches (`FR-PORTIFY-WORKFLOW.1`)
3. Implement `sc:` prefix stripping with empty-after-strip guard → `ERR_TARGET_NOT_FOUND` (`FR-PORTIFY-WORKFLOW.1`)
4. Implement empty/whitespace/None guard → `ERR_TARGET_NOT_FOUND` (`FR-PORTIFY-WORKFLOW.1`)
5. Implement ambiguity detection → `ERR_AMBIGUOUS_TARGET` with command-first policy (`FR-PORTIFY-WORKFLOW.1`)
6. Implement command → skill link via `## Activation` parsing with `Skill sc:<name>-protocol` pattern (`FR-PORTIFY-WORKFLOW.1`)
7. Implement skill → command backward-resolution via `sc-`/`-protocol` stripping heuristic (`FR-PORTIFY-WORKFLOW.1`)
8. Handle edge cases: standalone command (`skill=None`), standalone skill (`command=None`), multi-skill commands (primary only, secondaries warned) (`FR-PORTIFY-WORKFLOW.1`)

> **Architect focus**: Keep `resolution.py` pure — no side effects, no I/O beyond file reads. This makes it trivially testable and keeps the resolution algorithm deterministic. Log all resolution decisions (which input form was detected, why command-first policy was applied) for debugging user-reported issues.

**Validation gate**: Tests for all 6 input forms, all error codes, edge cases. Resolution completes <1s. Existing test suite passes.

---

## Phase 2: Integration — Discovery, Process, CLI

**Goal**: Wire resolution into the existing pipeline without breaking backward compatibility.

**Duration**: 8-12 hours (Session 2)

### Milestone 2.1: Component Discovery (`discover_components.py`)

*Can run in parallel with 2.2*

1. Implement agent extraction from SKILL.md using the 6 spec-defined `AGENT_PATTERNS` from the resolution algorithm (`FR-PORTIFY-WORKFLOW.2`):
   - Backtick-agent notation
   - YAML arrays
   - Spawn/delegate/invoke verbs
   - `uses` references
   - Model-parenthetical patterns
   - `agents/` path patterns
2. Build `ComponentTree` from resolved target (`FR-PORTIFY-WORKFLOW.2`)
3. Handle missing agents: `found=False`, emit warnings, continue (`FR-PORTIFY-WORKFLOW.2`)
4. Implement `--include-agent` deduplication with `referenced_in="cli-override"` precedence as part of Step R3 agent resolution, with test ownership in this milestone (`FR-PORTIFY-WORKFLOW.2`)

> **Architect focus**: Preserve one-way discovery depth. Avoid recursive agent-to-agent expansion in this release; it would alter scope and risk profile. Keep missing references observable but non-fatal.

**Validation gate**: Agent extraction tests against synthetic SKILL.md with all 6 patterns. Missing agent warning tests. Existing test suite passes.

### Milestone 2.2: Process Extension (`process.py`)

*Can run in parallel with 2.1*

1. Add `additional_dirs` parameter to `PortifyProcess` (`FR-PORTIFY-WORKFLOW.3`)
2. Build `--add-dir` args from `ComponentTree.all_source_dirs` with deduplication (`FR-PORTIFY-WORKFLOW.3`)
3. Implement directory cap at 10 with two-tier consolidation (`FR-PORTIFY-WORKFLOW.3`, `NFR-005`):
   - **Tier 1**: `os.path.commonpath()` to merge directories sharing common ancestors, but only when the common parent contains no more than 3x the total file count of its constituent directories
   - **Tier 2**: If still over cap after Tier 1, select top 10 by component count — deterministic, auditable, and ensures the most relevant directories survive
4. Record consolidation decisions in `resolution_log`
5. Verify `additional_dirs=None` preserves exact v2.24 behavior (SC-11)

> **Architect focus**: This is a containment boundary, not a feature expansion point. The two-tier consolidation ensures robustness for skills referencing agents scattered across unrelated directories without deferring a known gap.

**Validation gate**: Process invocation tests with 0, 5, 15 directories. Consolidation logic tests including Tier 2 fallback. Existing test suite passes.

### Milestone 2.3: CLI & Config (`cli.py`, `config.py`)

*Depends on 2.1 and 2.2*

1. Change CLI argument from `WORKFLOW_PATH` to `TARGET` (`FR-PORTIFY-WORKFLOW.1`)
2. Add `--commands-dir`, `--skills-dir`, `--agents-dir` override options (`FR-PORTIFY-WORKFLOW.1`)
3. Add `--include-agent` option with empty-string filtering; keep CLI ownership limited to argument capture while the dedup algorithm remains in Step R3 discovery logic (`FR-PORTIFY-WORKFLOW.2`)
4. Add `--save-manifest` option (`FR-PORTIFY-WORKFLOW.2`)
5. Extend `load_portify_config()` with new parameter passthrough (`FR-PORTIFY-WORKFLOW.1`, `FR-PORTIFY-WORKFLOW.2`, `FR-PORTIFY-WORKFLOW.3`)
6. Extend `ValidateConfigResult` with `command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings` fields (`FR-PORTIFY-WORKFLOW.1`, `FR-PORTIFY-WORKFLOW.2`)

> **Architect focus**: CLI is the highest user-visible risk area. Minimize surprise by preserving existing success paths and keeping new behavior additive. Existing skill-directory inputs must resolve identically to v2.24.

**Validation gate**: CLI integration tests for all new options. Config round-trip tests. Existing test suite passes.

---

## Phase 3: Validation, Artifacts & Compatibility Proof

**Goal**: Full test coverage, artifact enrichment, backward-compatibility proof.

**Duration**: 5-6 hours (Session 3)

### Milestone 3.1: Validation Extension (`validate_config.py`)

1. Add check 5: command → skill link validity (`FR-PORTIFY-WORKFLOW.1` / `FR-PORTIFY-WORKFLOW.2`)
2. Add check 6: referenced agent existence (`FR-PORTIFY-WORKFLOW.2`)
3. Extend `to_dict()` with all new fields required by the spec, including `warnings`, `command_path`, `skill_dir`, `target_type`, and `agent_count`; treat completeness here as mandatory because downstream contract/resume telemetry would otherwise lose data silently

> **Architect focus**: Validation should encode system invariants, not only user messaging. The enriched checks improve traceability for debugging and future v2.25 expansion.

### Milestone 3.2: Artifact Enrichment

1. Enrich `component-inventory.md` with a Command section, Agents table, Cross-Tier Data Flow section, Resolution Log section, and explicit frontmatter fields: `source_command`, `source_skill`, `component_count`, `total_lines`, `agent_count`, `has_command`, `has_skill`, `duration_seconds` (`FR-PORTIFY-WORKFLOW.2`)

### Milestone 3.3: Full Test Suite & Backward Compatibility

Organized into four validation streams for clarity:

#### Stream A — Unit Validation
- Resolver tests for all 6 input forms and all failure modes
- Model conversion and round-trip tests
- Regex extraction tests (all 6 agent patterns)
- Directory consolidation tests (both tiers)

#### Stream B — Integration Validation
- CLI invocation tests with new and legacy inputs
- Validation result shape tests
- Manifest and inventory artifact tests
- Process invocation tests with and without `additional_dirs`

#### Stream C — Regression Validation
- Existing suite passes unchanged (zero modifications)
- Old skill-directory flows match prior behavior exactly
- No changes under restricted directories: `pipeline/`, `sprint/`

#### Stream D — Non-Functional Verification
- Resolution timing under 1 second (`time.monotonic()` assertions)
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns empty (NFR-003)
- `git diff --name-only` against `pipeline/` and `sprint/` shows no changes (NFR-002)
- Directory cap respected with >10 dirs input (NFR-005)

**Validation gate**: All 12 success criteria verified. All ~37 new tests pass. Full existing test suite green.

---

## Risk Assessment & Mitigation

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|-------------|------------|-------|
| 1 | Backward-compat break from TARGET arg change | High | Low | Preserve `resolve_workflow_path()` unchanged; skill-directory inputs route through backward path; existing fixtures as regression tests; continuous testing gate at every milestone | 2.3 |
| 2 | Resolution ambiguity or unstable precedence | High | Low | Encode precedence centrally in `resolution.py`; test same-class ambiguity separately from cross-class command-first precedence; descriptive typed errors | 1.2 |
| 3 | Agent regex misses references | Medium | Medium | `--include-agent` escape hatch; iterate patterns post-release; corpus-style tests covering each pattern | 2.1 |
| 4 | Subprocess `--add-dir` overflow | Medium | Low | Cap at 10 with two-tier consolidation (commonpath + top-10-by-component-count); resolution_log audit trail | 2.2 |
| 5 | Skill → command reverse-resolution fragile | Low | Medium | Missing command = warning only, pipeline continues with `command=None` | 1.2 |
| 6 | Non-standard project layout causes root detection failure | Low | Medium | `--commands-dir`/`--skills-dir`/`--agents-dir` explicit overrides; actionable error messages | 2.3 |
| 7 | CLI contract drift confuses current users | Medium | Medium | Keep current usage forms working; explicit help text for all accepted target types; test both new and legacy invocation patterns | 2.3 |
| 8 | YAML frontmatter parse failure | Low | Low | Graceful degradation to convention-based discovery | 1.2 |

**Highest-priority mitigation**: Risk 1 (backward compat). Addressed structurally by the continuous testing gate established in Milestone 1.0 — existing tests must pass at every milestone, not just Phase 3.

---

## Resource Requirements & Dependencies

### Internal Dependencies (Modification Order)

```
models.py ──────────┐
                     ├──→ discover_components.py ──┐
resolution.py ──────┘         (2.1)                ├──→ cli.py + config.py ──→ validate_config.py
                     ┌──→ process.py ──────────────┘         (2.3)                 (3.1)
                     │         (2.2)
models.py ───────────┘
```

- `models.py` and `resolution.py` are independent — build in parallel (Phase 1)
- `discover_components.py` and `process.py` depend on models — build in parallel (Phase 2, milestones 2.1 ∥ 2.2)
- `cli.py` and `config.py` depend on all above — sequential (Phase 2, milestone 2.3)
- `validate_config.py` depends on all above — sequential (Phase 3)

### External Dependencies

| Dependency | Risk | Notes |
|------------|------|-------|
| Click framework | None | Stable, only additive option changes |
| Python `re` | None | Stdlib, no version concerns |
| Python `os.path.commonpath()` | None | Stdlib, Python 3.5+ |
| Existing `ComponentEntry`/`ComponentInventory` | Low | Extended, not modified |
| Existing `ClaudeProcess` | Low | Subclass extension only |
| Existing `validate_config.py` | Low | Additive checks only |

### Engineering Resources

- **Primary implementer**: Python CLI and dataclass modeling, path resolution, compatibility-focused development
- **Reviewer**: Regression review, CLI/UX review, artifact semantics check
- **QA support**: Edge-case scenario validation, timing and compatibility confirmation

---

## Success Criteria & Validation Approach

| # | Criterion | Test Method | Phase |
|---|-----------|-------------|-------|
| SC-1 | `resolve_target("roadmap")` resolves correctly <1s | Unit test with timing assertion | 1.2 |
| SC-2 | `resolve_target("sc:roadmap")` strips prefix | Unit test | 1.2 |
| SC-3 | Skill-directory backward resolution | Unit test | 1.2 |
| SC-4 | `ERR_TARGET_NOT_FOUND` for nonexistent | Unit test | 1.2 |
| SC-5 | `ComponentTree` correctness | Integration test | 2.1 |
| SC-6 | All 6 regex patterns match | Unit test with synthetic SKILL.md | 2.1 |
| SC-7 | `--include-agent` dedup | Unit test for Step R3 dedup algorithm; optional CLI invocation coverage may be added separately | 2.1 |
| SC-8 | Missing agents warn, don't fail | Unit test | 2.1 |
| SC-9 | `to_flat_inventory()` equivalence | Comparison test against existing output | 3.3 |
| SC-10 | All existing tests pass unchanged | Full `uv run pytest` | 3.3 |
| SC-11 | `additional_dirs=None` preserves v2.24 | Process invocation test | 2.2 |
| SC-12 | ~37 new tests pass | Full `uv run pytest` | 3.3 |

### Release Gate

Do not mark the release complete until:
1. All new tests pass (Streams A & B)
2. All existing tests pass unchanged (Stream C)
3. Backward-compatibility evidence is recorded (Stream C)
4. Directory cap behavior is deterministic and logged (Stream D)
5. Warning/error semantics are stable and documented through tests
6. No `async def`/`await` in new code (Stream D)
7. No `pipeline/`/`sprint/` modifications (Stream D)

---

## Timeline Estimates

| Phase | Scope | Hours | Session |
|-------|-------|-------|---------|
| Phase 1 | Pre-work + Models + Resolution | 6-10h | Session 1 |
| Phase 2 | Discovery + Process + CLI | 8-12h | Session 2 |
| Phase 3 | Validation + Artifacts + Proof | 5-6h | Session 3 |
| **Total** | | **19-28h** | **3 sessions** |

### Milestone Checkpoints

- **Checkpoint A** (end of Phase 1): Models + resolver stable, all 6 input forms resolve correctly
- **Checkpoint B** (end of Phase 2): Component tree + process integration + CLI stable
- **Checkpoint C** (end of Phase 3): All validation streams green, regression and NFR proof complete

---

## Architectural Recommendations

1. **Keep `resolution.py` pure**: No side effects, no I/O beyond file reads. This makes it trivially testable and keeps the resolution algorithm deterministic.

2. **Boundary conversion in `to_flat_inventory()` only**: The `Path` → `str` conversion should happen at exactly one point. Don't leak `Path` objects into existing code that expects `str`.

3. **Regex patterns as module constants**: Keep the 6 `AGENT_PATTERNS` aligned to the resolution algorithm in `resolution.py` per the spec. If implementation later places compiled `re.Pattern` constants in `discover_components.py` for performance or organization, document that as a deliberate implementation choice rather than the normative spec shape.

4. **Continuous testing as a structural gate**: Run `uv run pytest` at every milestone boundary. A milestone is not complete until existing tests pass. This is not advisory — it is the primary safety net against backward-compatibility regressions.

5. **Log resolution decisions**: The `resolution_log` in directory consolidation is good. Extend this pattern to all resolution decisions (which input form was detected, why command-first policy was applied, etc.). This is invaluable for debugging user-reported issues.

---

## Deferred Items (v2.25+)

These are explicitly out of scope per the spec's open questions:

1. **Recursive agent-to-agent resolution** (OI-1) — current: O(1)-depth only
2. **`--manifest` load support** (OI-2) — current: write-only via `--save-manifest`
3. **`--exclude-component` filtering** (OI-3)
4. **Quality scores for this spec** (OI-4)

Roadmap-originated observations for a future release (not spec-defined open items):
- Multi-source agent tracking — current: first source wins
- Configurable consolidation threshold — current: hardcoded cap at 10
