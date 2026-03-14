

---
validation_milestones: 8
interleave_ratio: '1:1'
---

# Test Strategy — v2.24.1 CLI Portify v5

## 1. Validation Milestones Mapped to Roadmap Phases

### Phase 1: Foundation

**VM-1: Pre-work Verification** (Milestone 1.0)
- Confirm existing test suite baseline: `uv run pytest` passes, record test count and timing
- Verify no files in `pipeline/` or `sprint/` are staged for modification
- Document current coverage for `cli_portify/` modules

**VM-2: Data Models** (Milestone 1.1)
- `ResolvedTarget` dataclass construction with all field combinations
- `CommandEntry`, `SkillEntry`, `AgentEntry` construction and field validation
- `ComponentTree` computed properties (`component_count`, `total_lines`, `all_source_dirs`)
- `to_flat_inventory()` round-trip: `ComponentTree` → `ComponentInventory` → verify equivalence
- `to_manifest_markdown()` produces valid Markdown with expected sections
- Error code constants are unique and non-empty strings

**VM-3: Resolution Algorithm** (Milestone 1.2)
- All 6 input forms resolve correctly (bare name, prefixed, command path, skill dir path, skill dir name, SKILL.md path)
- `sc:` prefix stripping including `"sc:"` → `ERR_TARGET_NOT_FOUND`
- Empty/whitespace/None → `ERR_TARGET_NOT_FOUND`
- Ambiguity detection → `ERR_AMBIGUOUS_TARGET` with command-first policy
- Command → skill link via `## Activation` parsing
- Skill → command backward-resolution via `sc-`/`-protocol` stripping
- Edge cases: standalone command, standalone skill, multi-skill commands
- Resolution timing <1s via `time.monotonic()`

### Phase 2: Integration

**VM-4: Component Discovery** (Milestone 2.1)
- Agent extraction hits all 6 regex patterns against synthetic SKILL.md fixtures
- `ComponentTree` built correctly from resolved targets
- Missing agents: `found=False`, warnings emitted, no pipeline failure
- `--include-agent` deduplication with `cli-override` precedence

**VM-5: Process Extension** (Milestone 2.2)
- `additional_dirs=None` produces identical behavior to v2.24 (`PortifyProcess` unchanged)
- `additional_dirs` with 0, 5, 10 directories: correct `--add-dir` arg construction
- Directory cap: 15 dirs → Tier 1 consolidation via `commonpath()` → verify ≤10
- Tier 2 fallback: commonpath insufficient → top 10 by component count
- `resolution_log` records consolidation decisions

**VM-6: CLI & Config** (Milestone 2.3)
- CLI accepts all 6 target forms as the `TARGET` argument
- `--commands-dir`, `--skills-dir`, `--agents-dir` override auto-detection
- `--include-agent` with valid names, duplicates, and empty strings
- `--save-manifest` writes Markdown artifact to specified path
- `load_portify_config()` passes new parameters through correctly
- `ValidateConfigResult` includes new fields in construction and `to_dict()`

### Phase 3: Validation & Proof

**VM-7: Validation Extension** (Milestone 3.1–3.2)
- Check 5: command → skill link validity catches broken links
- Check 6: referenced agent existence catches missing agents
- Enriched `component-inventory.md` contains all new sections and frontmatter fields

**VM-8: Full Compatibility Proof** (Milestone 3.3)
- All ~37 new tests pass
- All pre-existing tests pass unchanged (zero modifications to existing test files)
- `grep -r "async def\|await" src/superclaude/cli/cli_portify/` returns empty
- `git diff --name-only` shows no `pipeline/` or `sprint/` changes
- Directory cap enforced with >10 dirs input

---

## 2. Test Categories

### Unit Tests (~22 tests)

| Area | Tests | Priority |
|------|-------|----------|
| `ResolvedTarget` construction | 2 | High |
| `ComponentTree` properties | 3 | High |
| `to_flat_inventory()` conversion | 2 | Critical |
| `to_manifest_markdown()` output | 1 | Medium |
| Error code constants | 1 | Low |
| Input classification (6 forms) | 6 | Critical |
| Prefix stripping + guards | 3 | High |
| Ambiguity detection + command-first | 2 | Critical |
| Agent regex patterns (6 patterns) | 6 | High |
| Directory consolidation (Tier 1 + 2) | 3 | High |
| Skill → command backward-resolution | 2 | Medium |

### Integration Tests (~10 tests)

| Area | Tests | Priority |
|------|-------|----------|
| CLI invocation with new target forms | 3 | Critical |
| CLI invocation with legacy skill-dir | 1 | Critical |
| Process with `additional_dirs` | 2 | High |
| Validation checks 5-6 | 2 | High |
| Config round-trip | 1 | Medium |
| Manifest artifact write | 1 | Medium |

### Regression Tests (~3 tests)

| Area | Tests | Priority |
|------|-------|----------|
| Existing test suite passes unchanged | 1 | Critical |
| Old skill-directory flows identical | 1 | Critical |
| `resolve_workflow_path()` untouched | 1 | Critical |

### Non-Functional / Acceptance Tests (~4 tests)

| Area | Tests | Priority |
|------|-------|----------|
| Resolution <1s timing assertion | 1 | High |
| No async code (`grep` check) | 1 | Critical |
| No pipeline/sprint modifications | 1 | Critical |
| Directory cap at 10 | 1 | High |

---

## 3. Test-Implementation Interleaving Strategy

The ratio is **1:1** — each milestone produces tests alongside or immediately after its implementation. This is driven by the roadmap's own constraint: *"A milestone is not complete until existing tests pass."*

### Interleaving Schedule

```
Phase 1:
  M1.0: [baseline test run] ─────────────────── Gate: existing tests pass
  M1.1: [implement models] → [write unit tests] ── Gate: models + existing pass
  M1.2: [implement resolver] → [write unit tests] ── Gate: resolver + models + existing pass

Phase 2:
  M2.1: [implement discovery] → [write unit tests] ── Gate: all prior + existing pass
  M2.2: [implement process] → [write unit tests] ──── Gate: all prior + existing pass
  M2.3: [implement CLI] → [write integration tests] ─ Gate: all prior + existing pass

Phase 3:
  M3.1: [implement validation] → [write tests] ────── Gate: all prior + existing pass
  M3.2: [implement artifacts] → [write tests] ──────── Gate: all prior + existing pass
  M3.3: [regression + NFR tests] ─────────────────── Gate: ALL tests green
```

### Rules

1. **No milestone advances without green tests.** Run `uv run pytest` at every boundary.
2. **Write tests for each module before moving to the next module.** Do not batch test writing to Phase 3.
3. **Regression tests run continuously**, not just in Phase 3 — they are part of every gate.
4. **Parallel milestones (2.1 ∥ 2.2)**: each writes its own tests independently; both must pass before 2.3 starts.

---

## 4. Risk-Based Test Prioritization

Ordered by `severity × probability × blast_radius`:

| Priority | Risk | Test Focus | When |
|----------|------|------------|------|
| P0 | Backward-compat break (Risk 1) | Legacy skill-dir inputs produce identical results; existing test suite untouched | Every milestone gate |
| P0 | No pipeline/sprint modifications (NFR-002) | `git diff` assertion | Every milestone gate |
| P1 | Resolution ambiguity (Risk 2) | All 6 input forms; same-class ambiguity; cross-class command-first | M1.2 |
| P1 | CLI argument change (Risk 7) | Both new and legacy invocation patterns | M2.3 |
| P2 | Agent regex misses (Risk 3) | All 6 patterns against synthetic corpus; `--include-agent` escape | M2.1 |
| P2 | Subprocess overflow (Risk 4) | 10+ directory inputs; both consolidation tiers | M2.2 |
| P3 | Reverse-resolution fragile (Risk 5) | Non-standard naming; missing command → warning only | M1.2 |
| P3 | Root detection failure (Risk 6) | Non-standard layout + explicit overrides | M2.3 |
| P3 | YAML frontmatter failure (Risk 8) | Malformed frontmatter → graceful degradation | M1.2 |

---

## 5. Acceptance Criteria Per Milestone

### M1.0 — Pre-work
- [ ] Existing `uv run pytest` passes — baseline count and timing recorded
- [ ] Change map document lists all impacted files
- [ ] Compatibility checklist confirms no pipeline/sprint edits planned

### M1.1 — Data Models
- [ ] All dataclass constructors work with valid and edge-case inputs
- [ ] `to_flat_inventory()` output matches `ComponentInventory` structure exactly
- [ ] `component_count` and `total_lines` compute correctly for multi-component trees
- [ ] Existing tests still pass

### M1.2 — Resolution Algorithm
- [ ] 6/6 input forms resolve to correct `ResolvedTarget`
- [ ] All 4 error codes triggered by appropriate inputs
- [ ] Command-first policy applied for ambiguous bare names
- [ ] `## Activation` parsing extracts skill reference correctly
- [ ] Resolution timing <1s (measured, not estimated)
- [ ] Existing tests still pass

### M2.1 — Component Discovery
- [ ] 6/6 regex patterns match in synthetic SKILL.md
- [ ] Missing agent → `found=False` + warning, no failure
- [ ] `--include-agent` deduplicates correctly with `cli-override` precedence
- [ ] Existing tests still pass

### M2.2 — Process Extension
- [ ] `additional_dirs=None` → v2.24-identical `PortifyProcess` invocation
- [ ] 15 directories → consolidated to ≤10 with `resolution_log` entries
- [ ] Tier 2 fallback selects top 10 by component count
- [ ] Existing tests still pass

### M2.3 — CLI & Config
- [ ] `superclaude portify roadmap` resolves same as `superclaude portify src/.../sc-roadmap-protocol/`
- [ ] Override flags (`--commands-dir`, etc.) change resolution paths
- [ ] `--save-manifest` writes valid Markdown file
- [ ] `ValidateConfigResult.to_dict()` includes all new fields
- [ ] Existing tests still pass

### M3.1–3.2 — Validation & Artifacts
- [ ] Broken command → skill link detected by check 5
- [ ] Missing agent detected by check 6
- [ ] Enriched inventory artifact contains all required sections

### M3.3 — Full Proof
- [ ] All ~37 new tests pass
- [ ] All pre-existing tests pass (zero test file modifications)
- [ ] `grep -r "async def\|await" src/superclaude/cli/cli_portify/` → empty
- [ ] `git diff --name-only` → no pipeline/ or sprint/ files
- [ ] 12/12 success criteria verified

---

## 6. Quality Gates Between Phases

### Gate 1: Phase 1 → Phase 2

| Check | Method | Blocking? |
|-------|--------|-----------|
| All model unit tests pass | `uv run pytest tests/cli_portify/test_models.py` | Yes |
| All resolver unit tests pass | `uv run pytest tests/cli_portify/test_resolution.py` | Yes |
| Existing test suite green | `uv run pytest` (full) | Yes |
| No async code introduced | `grep -r "async def\|await" src/superclaude/cli/cli_portify/` | Yes |
| Resolution <1s for all 6 forms | Timing assertions in test suite | Yes |

### Gate 2: Phase 2 → Phase 3

| Check | Method | Blocking? |
|-------|--------|-----------|
| All Phase 1 + Phase 2 tests pass | `uv run pytest tests/cli_portify/` | Yes |
| Existing test suite green | `uv run pytest` (full) | Yes |
| Legacy skill-dir CLI invocation identical | Integration test comparison | Yes |
| No pipeline/sprint modifications | `git diff --name-only \| grep -E "pipeline/\|sprint/"` → empty | Yes |
| Directory consolidation deterministic | Unit test with fixed input → fixed output | Yes |

### Gate 3: Release Gate (after Phase 3)

| Check | Method | Blocking? |
|-------|--------|-----------|
| All ~37 new tests pass (Streams A+B) | `uv run pytest tests/cli_portify/ -v` | Yes |
| All existing tests unchanged (Stream C) | `uv run pytest` + `git diff tests/` shows no existing test edits | Yes |
| NFR verification (Stream D) | 4 dedicated NFR tests | Yes |
| 12/12 success criteria met | Manual checklist sign-off | Yes |
| No TODO/stub/mock in new code | `grep -r "TODO\|NotImplemented\|mock" src/superclaude/cli/cli_portify/` | Yes |
| Warning/error messages tested | Unit tests assert exact error codes and message content | Yes |

---

## Test File Organization

```
tests/cli_portify/
├── test_models.py              # VM-2: dataclass construction, conversion, properties
├── test_resolution.py          # VM-3: 6 input forms, errors, edge cases, timing
├── test_discover_components.py # VM-4: regex patterns, ComponentTree, missing agents
├── test_process.py             # VM-5: additional_dirs, consolidation, cap
├── test_cli_integration.py     # VM-6: CLI invocation, options, config
├── test_validation.py          # VM-7: checks 5-6, enriched artifacts
├── test_regression.py          # VM-8: backward compat, existing behavior preservation
└── test_nfr.py                 # VM-8: async check, pipeline/sprint check, timing
```
