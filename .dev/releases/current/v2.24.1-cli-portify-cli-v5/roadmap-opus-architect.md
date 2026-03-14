

---
spec_source: "portify-release-spec.md"
complexity_score: 0.65
primary_persona: architect
---

# v2.24.1 CLI Portify v5 — Project Roadmap

## Executive Summary

This release extends the CLI Portify pipeline with a unified target resolution system, replacing the single skill-directory input with 6 input forms (bare name, prefixed name, command path, skill directory path, skill directory name, SKILL.md path). The core addition is `resolution.py` (~350-450 lines) plus additive modifications to 6 existing modules. Architecture is constrained to synchronous, backward-compatible changes with zero modifications to `pipeline/` or `sprint/` base modules.

**Scope**: 23 requirements (18 functional, 5 non-functional), 4 domains (resolution, discovery, CLI, validation), ~37 new tests.

**Estimated effort**: 19-28 hours across 3 phases.

---

## Phase 1: Foundation — Models & Resolution Core

**Goal**: Establish data models and the deterministic resolution algorithm.

**Duration**: 6-10 hours

### Milestone 1.1: Data Models (`models.py`)

1. Define `ResolvedTarget` dataclass with `command_path: Path | None`, `skill_dir: Path | None`, `project_root: Path`, `target_type: str`
2. Define `CommandEntry` (Tier 0), `SkillEntry` (Tier 1), `AgentEntry` (Tier 2) dataclasses
3. Define `ComponentTree` with `command`, `skill`, `agents` fields plus `component_count`, `total_lines`, `all_source_dirs` computed properties
4. Implement `to_flat_inventory()` → backward-compatible `ComponentInventory` conversion (`Path` → `str` at boundary)
5. Implement `to_manifest_markdown()` → human-readable Markdown output
6. Add error code constants: `ERR_TARGET_NOT_FOUND`, `ERR_AMBIGUOUS_TARGET`, `ERR_BROKEN_ACTIVATION`, `WARN_MISSING_AGENTS`

**Validation gate**: Unit tests for all dataclass construction, `to_flat_inventory()` round-trip, error code values.

### Milestone 1.2: Resolution Algorithm (`resolution.py`)

1. Implement `resolve_target(target: str, ...) → ResolvedTarget` with `time.monotonic()` timing (FR-001, NFR-001)
2. Implement input classification: detect which of 6 forms the input matches
3. Implement `sc:` prefix stripping with empty-after-strip guard → `ERR_TARGET_NOT_FOUND` (FR-002)
4. Implement empty/whitespace/None guard → `ERR_TARGET_NOT_FOUND` (FR-003)
5. Implement ambiguity detection → `ERR_AMBIGUOUS_TARGET` with command-first policy (FR-004)
6. Implement command → skill link via `## Activation` parsing with `Skill sc:<name>-protocol` pattern (FR-005)
7. Implement skill → command backward-resolution via `sc-`/`-protocol` stripping heuristic (FR-006)
8. Handle edge cases: standalone command (`skill=None`), standalone skill (`command=None`), multi-skill commands (primary only, secondaries warned) (FR-018)

**Validation gate**: Tests for all 6 input forms, all error codes, edge cases. Resolution completes <1s.

---

## Phase 2: Integration — Discovery, Process, CLI

**Goal**: Wire resolution into existing pipeline without breaking backward compatibility.

**Duration**: 8-12 hours

### Milestone 2.1: Component Discovery (`discover_components.py`)

*Can run in parallel with 2.2*

1. Implement agent extraction from SKILL.md using 6 regex patterns (FR-008):
   - Backtick-agent notation
   - YAML arrays
   - Spawn/delegate/invoke verbs
   - `uses` references
   - Model-parenthetical patterns
   - `agents/` path patterns
2. Build `ComponentTree` from resolved target (FR-007)
3. Handle missing agents: `found=False`, emit warnings, continue (FR-010)
4. Implement `--include-agent` deduplication with `referenced_in="cli-override"` precedence (FR-009)

**Validation gate**: Agent extraction tests against synthetic SKILL.md with all 6 patterns. Missing agent warning tests.

### Milestone 2.2: Process Extension (`process.py`)

*Can run in parallel with 2.1*

1. Add `additional_dirs` parameter to `PortifyProcess` (FR-013)
2. Build `--add-dir` args from `ComponentTree.all_source_dirs` with deduplication
3. Implement directory cap at 10 with consolidation via `os.path.commonpath()` (FR-014, NFR-005)
4. Record consolidation decisions in `resolution_log`
5. Verify `additional_dirs=None` preserves exact v2.24 behavior (SC-11)

**Validation gate**: Process invocation tests with 0, 5, 15 directories. Consolidation logic tests.

### Milestone 2.3: CLI & Config (`cli.py`, `config.py`)

*Depends on 2.1 and 2.2*

1. Change CLI argument from `WORKFLOW_PATH` to `TARGET` (FR-001)
2. Add `--commands-dir`, `--skills-dir`, `--agents-dir` override options (FR-015)
3. Add `--include-agent` option with empty-string filtering (FR-009)
4. Add `--save-manifest` option (FR-012)
5. Extend `load_portify_config()` with new parameter passthrough (FR-016)
6. Extend `ValidateConfigResult` with `command_path`, `skill_dir`, `target_type`, `agent_count`, `warnings` fields (FR-016)

**Validation gate**: CLI integration tests for all new options. Config round-trip tests.

---

## Phase 3: Validation & Artifacts

**Goal**: Full test coverage, artifact enrichment, backward-compatibility proof.

**Duration**: 5-6 hours

### Milestone 3.1: Validation Extension (`validate_config.py`)

1. Add check 5: command → skill link validity (FR-016)
2. Add check 6: referenced agent existence (FR-016)
3. Extend `to_dict()` with new fields

### Milestone 3.2: Artifact Enrichment

1. Enrich `component-inventory.md` with Command section, Agents table, Cross-Tier Data Flow, Resolution Log, extended frontmatter (FR-017)

### Milestone 3.3: Full Test Suite & Backward Compatibility

1. Write ~37 new tests covering all resolution paths, edge cases, integration
2. Run existing test suite unchanged — all must pass (NFR-004)
3. Verify zero modifications to `pipeline/` or `sprint/` via `git diff --name-only` (NFR-002)
4. Verify no `async def` or `await` in new code via `grep -r` (NFR-003)

**Validation gate**: All 12 success criteria verified. Full test suite green.

---

## Risk Assessment & Mitigation

| # | Risk | Severity | Probability | Mitigation | Phase |
|---|------|----------|-------------|------------|-------|
| 1 | Agent regex misses references | Medium | Medium | `--include-agent` escape hatch; iterate patterns post-release | 2.1 |
| 2 | Backward-compat break from TARGET arg change | High | Low | Preserve `resolve_workflow_path()` unchanged; skill-directory inputs route through backward path; existing fixtures as regression tests | 2.3 |
| 3 | Subprocess `--add-dir` overflow | Medium | Low | Cap at 10 with `commonpath()` consolidation | 2.2 |
| 4 | YAML frontmatter parse failure | Low | Low | Graceful degradation to convention-based discovery | 1.2 |
| 5 | Project root detection in non-standard layouts | Low | Medium | `--commands-dir`/`--skills-dir`/`--agents-dir` explicit overrides | 2.3 |
| 6 | Skill → command reverse-resolution fragile | Low | Medium | Missing command = warning only, pipeline continues with `command=None` | 1.2 |

**Highest-priority mitigation**: Risk 2 (backward compat). Address by running existing test suite as a gate at every milestone, not just Phase 3.

---

## Resource Requirements & Dependencies

### Internal Dependencies (Modification Order)

```
models.py ──────────┐
                     ├──→ discover_components.py ──┐
resolution.py ──────┘                              ├──→ cli.py + config.py ──→ validate_config.py
                     ┌──→ process.py ──────────────┘
                     │
models.py ───────────┘
```

- `models.py` and `resolution.py` are independent — build in parallel (Phase 1)
- `discover_components.py` and `process.py` depend on models — build in parallel (Phase 2)
- `cli.py` and `config.py` depend on all above — sequential (Phase 2, late)

### External Dependencies

| Dependency | Risk | Notes |
|------------|------|-------|
| Click framework | None | Stable, only additive option changes |
| Python `re` | None | Stdlib, no version concerns |
| Python `os.path.commonpath()` | None | Stdlib, Python 3.5+ |
| Existing `ComponentEntry`/`ComponentInventory` | Low | Extended, not modified |
| Existing `ClaudeProcess` | Low | Subclass extension only |
| Existing `validate_config.py` | Low | Additive checks only |

---

## Success Criteria Validation Approach

| # | Criterion | Test Method | Phase |
|---|-----------|-------------|-------|
| SC-1 | `resolve_target("roadmap")` resolves correctly <1s | Unit test with timing assertion | 1.2 |
| SC-2 | `resolve_target("sc:roadmap")` strips prefix | Unit test | 1.2 |
| SC-3 | Skill-directory backward resolution | Unit test | 1.2 |
| SC-4 | `ERR_TARGET_NOT_FOUND` for nonexistent | Unit test | 1.2 |
| SC-5 | `ComponentTree` correctness | Integration test | 2.1 |
| SC-6 | All 6 regex patterns match | Unit test with synthetic SKILL.md | 2.1 |
| SC-7 | `--include-agent` dedup | Unit test | 2.3 |
| SC-8 | Missing agents warn, don't fail | Unit test | 2.1 |
| SC-9 | `to_flat_inventory()` equivalence | Comparison test against existing output | 3.3 |
| SC-10 | All existing tests pass unchanged | Full `uv run pytest` | 3.3 |
| SC-11 | `additional_dirs=None` preserves v2.24 | Process invocation test | 2.2 |
| SC-12 | ~37 new tests pass | Full `uv run pytest` | 3.3 |

### Non-Functional Verification

- **NFR-001**: `time.monotonic()` assertions in resolution tests
- **NFR-002**: `git diff --name-only` against `pipeline/` and `sprint/` in CI
- **NFR-003**: `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns empty
- **NFR-004**: Existing test suite green with zero modifications
- **NFR-005**: Directory cap integration test with >10 dirs input

---

## Deferred Items (v2.25+)

These are explicitly out of scope per the spec's open questions:

1. **Recursive agent-to-agent resolution** (OI-1) — current: O(1)-depth only
2. **`--manifest` load support** (OI-2) — current: write-only via `--save-manifest`
3. **`--exclude-component` filtering** (OI-3)
4. **Multi-source agent tracking** (OI-5) — current: first source wins
5. **Configurable consolidation threshold** (OI-6) — current: hardcoded 3x rule

---

## Architectural Recommendations

1. **Keep `resolution.py` pure**: No side effects, no I/O beyond file reads. This makes it trivially testable and keeps the resolution algorithm deterministic.

2. **Boundary conversion in `to_flat_inventory()` only**: The `Path` → `str` conversion should happen at exactly one point. Don't leak `Path` objects into existing code that expects `str`.

3. **Regex patterns as module constants**: Define the 6 agent-extraction patterns as compiled `re.Pattern` constants at module level in `discover_components.py`. This aids both performance and maintainability.

4. **Run existing tests at every milestone**: Don't wait for Phase 3 to catch backward-compatibility regressions. The existing suite is your primary safety net — run it continuously.

5. **Log resolution decisions**: The `resolution_log` in directory consolidation is good. Extend this pattern to all resolution decisions (which input form was detected, why a command-first policy was applied, etc.). This is invaluable for debugging user-reported issues.
