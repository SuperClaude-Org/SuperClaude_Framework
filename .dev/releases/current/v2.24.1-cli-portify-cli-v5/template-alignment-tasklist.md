---
title: "Template Alignment Tasklist: Synthesized Spec -> Release Spec Template"
source_spec: synthesized-spec.md
target_template: src/superclaude/examples/release-spec-template.md
spec_type: portification
total_tasks: 27
content_preservation: 100%
---

# Template Alignment Tasklist

Restructure `synthesized-spec.md` to match `release-spec-template.md` while retaining 100% of existing content. This is a **structural refactoring** — no content is deleted, only reorganized.

## Structural Diff Summary

| Template Section | Current Spec Section | Status | Action |
|---|---|---|---|
| YAML frontmatter block | Lines 1-8 (plain markdown) | MISALIGNED | Rewrite as YAML code block with all required fields |
| 1. Problem Statement | 1. Problem Statement | PARTIAL | Add subsections 1.1 Evidence, 1.2 Scope Boundary |
| 2. Solution Overview | 2. Solution Overview | PARTIAL | Rename subsections to 2.1 Key Design Decisions (table format), 2.2 Workflow/Data Flow |
| 3. Functional Requirements | 3. Detailed Design (wrong content) | MISSING | Extract FRs from Section 3's detailed design content |
| 4. Architecture | 4. Module-Level Implementation Plan | MISALIGNED | Restructure into 4.1 New Files, 4.2 Modified Files, 4.3 Removed Files, 4.4 Module Dep Graph, 4.5 Data Models, 4.6 Implementation Order |
| 5. Interface Contracts | (not present) | MISSING | Create from CLI changes in 3.1.2 and gate info |
| 6. Non-Functional Requirements | (not present) | MISSING | Extract from scattered performance/constraint mentions |
| 7. Risk Assessment | 8. Risk Assessment | WRONG NUMBER | Renumber to 7 |
| 8. Test Plan | 5. Test Plan | WRONG NUMBER | Renumber to 8, add subsections 8.1/8.2/8.3 |
| 9. Migration & Rollout | 6. Migration and Backward Compatibility | WRONG NUMBER | Renumber to 9, add rollback plan |
| 10. Downstream Inputs | (not present) | MISSING | Create — describe how output feeds sc:roadmap and sc:tasklist |
| 11. Open Items | 10. Open Questions (Resolved) | WRONG NUMBER | Renumber to 11, convert to template table format |
| 12. Brainstorm Gap Analysis | (not present) | MISSING | Create — reference brainstorm from adversarial debate |
| Appendix A: Glossary | (not present) | MISSING | Create with domain terms |
| Appendix B: References | (not present) | MISSING | Create from cross-references |

---

## Task List

### Phase 1: Frontmatter and Header (Tasks 1-2)

#### T-01: Replace markdown header with YAML frontmatter block

**Current** (lines 1-8):
```
# Synthesized Spec: Command-Centric Resolution with Manifest Output
**Status**: FINAL SPEC (post-adversarial debate)
**Version**: v2.24.1-cli-portify-cli-v5
...
```

**Target**: Replace with YAML code block matching template:
```yaml
---
title: "Portification Enhancement: Full Workflow Resolution for cli-portify"
version: "1.0.0"
status: draft
feature_id: FR-PORTIFY-WORKFLOW
parent_feature: FR-PORTIFY-CLI
spec_type: portification
complexity_score: 0.65
complexity_class: moderate
target_release: v2.24.1
authors: [user, claude]
created: 2026-03-13
quality_scores:
  clarity: 0.0
  completeness: 0.0
  testability: 0.0
  consistency: 0.0
  overall: 0.0
---
```

**Notes**: Quality scores left at 0.0 — populated by spec-panel review later. Set `parent_feature: FR-PORTIFY-CLI` to link to v2.24. `status: draft` because quality scores are not yet populated.

#### T-02: Update document title line

Replace `# Synthesized Spec: Command-Centric Resolution with Manifest Output` with title derived from frontmatter. The YAML frontmatter IS the title — no separate H1 needed, OR keep a brief H1 like:

```markdown
# FR-PORTIFY-WORKFLOW: Full Workflow Resolution for cli-portify
```

Move the synthesis provenance metadata (Base, Incorporated from) to Appendix B: References.

---

### Phase 2: Section 1 — Problem Statement (Tasks 3-5)

#### T-03: Add Section 1.1 Evidence

**Source content**: The gap table on lines 15-19 already contains evidence. Reformat into the template's Evidence table:

```markdown
### 1.1 Evidence

| Evidence | Source | Impact |
|----------|--------|--------|
| `resolve_workflow_path()` requires `SKILL.md` in directory | `models.py:91-94` | Commands, agents excluded from portification input |
| `discover_components.py` scans only `SKILL.md`, `refs/`, `rules/`, `templates/`, `scripts/` | `steps/discover_components.py` | Agent delegation patterns, command frontmatter not inventoried |
| `PortifyProcess` passes `--add-dir` for 2 dirs only | `process.py` | Claude subprocesses cannot read command or agent files |
| `analysis-protocol.md` Step 1: "Find the Command" | `.claude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Protocol expects command discovery; runner doesn't perform it |
```

#### T-04: Add Section 1.2 Scope Boundary

**New content** (extract from current Section 7 Edge Cases and overall design scope):

```markdown
### 1.2 Scope Boundary

**In scope**:
- Accept command name, command path, skill directory, or skill name as input
- Resolve command -> skill -> agents component tree automatically
- Extend subprocess scoping to include all discovered component directories
- Backward compatibility with existing skill-directory input
- Escape hatches for manual agent inclusion (`--include-agent`)

**Out of scope**:
- Recursive agent-to-agent reference resolution (deferred to future release)
- Multi-skill command resolution beyond primary activation skill
- Manifest loading as an input mode (`--manifest` flag deferred)
- Code generation from the portification output
- Changes to `pipeline/` or `sprint/` base modules
```

#### T-05: Preserve existing problem statement prose

Keep the existing problem description text and gap table from current Section 1. The Evidence and Scope subsections are additive.

---

### Phase 3: Section 2 — Solution Overview (Tasks 6-8)

#### T-06: Restructure Key Design Decisions into template table format

**Current** (lines 52-58): Numbered list with bold headings.

**Target**: Convert to template's table format:

```markdown
### 2.1 Key Design Decisions

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Input entry point | Command-first, skill-fallback | Manifest-first (Approach B) | Simpler, 1 new file vs 4-5, no new pipeline step |
| Component tree model | In-memory ComponentTree | Persistent manifest file | Tree is transient; optional `--save-manifest` for debugging |
| Pipeline step count | No new steps (resolve in Step 1) | New Step 0 (Approach B) | Avoids step renumbering, resume logic changes |
| Resolution algorithm | Pure Python, deterministic | Claude-assisted discovery | <1s execution, no subprocess budget consumed |
| Agent discovery scope | O(1)-depth, SKILL.md only | Recursive agent-to-agent | Bounded complexity; escape hatch via --include-agent |
```

#### T-07: Rename "Architecture" subsection to "2.2 Workflow / Data Flow"

Keep the ASCII diagram from lines 31-50 as-is. Just change the heading from `### Architecture` to `### 2.2 Workflow / Data Flow`.

#### T-08: Preserve remaining Solution Overview prose

Keep the solution overview paragraph (line 27).

---

### Phase 4: Section 3 — Functional Requirements (Tasks 9-11)

#### T-09: Create FR-PORTIFY-WORKFLOW.1: Target Resolution

**Source**: Current Section 3.1 (Input Model) + Section 3.2 (Resolution Algorithm)

```markdown
### FR-PORTIFY-WORKFLOW.1: Multi-Form Target Resolution

**Description**: Accept 6 input forms (bare command name, prefixed name, command path, skill directory, skill name, SKILL.md path) and resolve to a normalized `ResolvedTarget` containing the command path, skill directory, and project root.

**Acceptance Criteria**:
- [ ] `resolve_target("roadmap")` resolves to command + skill + agents
- [ ] `resolve_target("sc:roadmap")` strips prefix and resolves identically
- [ ] `resolve_target("src/.../sc-roadmap-protocol/")` backward-resolves command
- [ ] `resolve_target("nonexistent")` returns `ERR_TARGET_NOT_FOUND`
- [ ] Resolution completes in <1s for all input forms
- [ ] `--commands-dir`, `--skills-dir`, `--agents-dir` override auto-detection

**Dependencies**: None
```

#### T-10: Create FR-PORTIFY-WORKFLOW.2: Full Component Tree Discovery

**Source**: Current Section 3.2 (Resolution Algorithm steps R3-R5) + Section 3.3 (ComponentTree) + Section 3.7 (discover_components changes)

```markdown
### FR-PORTIFY-WORKFLOW.2: Full Component Tree Discovery

**Description**: Build a hierarchical `ComponentTree` containing Tier 0 (command), Tier 1 (skill + refs/rules/templates/scripts), and agents. Enrich `component-inventory.md` with Command, Agents, and Data Flow sections.

**Acceptance Criteria**:
- [ ] `ComponentTree` contains `CommandEntry`, `SkillEntry`, `AgentEntry` for a standard workflow
- [ ] Agent extraction finds references matching 6 regex patterns in SKILL.md
- [ ] `--include-agent` adds manually specified agents to the tree
- [ ] Missing agents recorded with `found=False`, emitted as warnings, not errors
- [ ] `component-inventory.md` frontmatter includes `source_command`, `agent_count`, `has_command`
- [ ] `to_flat_inventory()` produces backward-compatible `ComponentInventory`
- [ ] `to_manifest_markdown()` produces readable Markdown (for `--save-manifest`)

**Dependencies**: FR-PORTIFY-WORKFLOW.1
```

#### T-11: Create FR-PORTIFY-WORKFLOW.3: Extended Subprocess Scoping

**Source**: Current Section 3.4 (Subprocess Scoping)

```markdown
### FR-PORTIFY-WORKFLOW.3: Extended Subprocess Scoping

**Description**: Extend `PortifyProcess` to pass all discovered component directories via `--add-dir`, enabling Claude subprocesses to read command files, agent definitions, and cross-skill references.

**Acceptance Criteria**:
- [ ] `PortifyProcess` accepts `additional_dirs` parameter
- [ ] `_build_add_dir_args()` includes all dirs from `ComponentTree.all_source_dirs`
- [ ] Duplicate directories are deduplicated
- [ ] >10 directories triggers consolidation warning
- [ ] `additional_dirs=None` preserves existing v2.24 behavior

**Dependencies**: FR-PORTIFY-WORKFLOW.2
```

---

### Phase 5: Section 4 — Architecture (Tasks 12-17)

#### T-12: Create Section 4.1 New Files

**Source**: Current Section 4.1 (lines 641-645)

Reformat into template table with Purpose and Dependencies columns.

#### T-13: Create Section 4.2 Modified Files

**Source**: Current Section 4.2 (lines 647-656)

Reformat into template table with Change and Rationale columns.

#### T-14: Create Section 4.3 Removed Files

Template marks this `[CONDITIONAL: refactoring, portification]`. Since `spec_type: portification`, include it.

**Content**: No files removed. State explicitly:

```markdown
### 4.3 Removed Files

No files are removed by this work. All existing modules are preserved with backward-compatible extensions.
```

#### T-15: Create Section 4.4 Module Dependency Graph

**Source**: Not present in current spec. Create from the module relationships described in Sections 3.5-3.7.

```
resolution.py ──> models.py (ResolvedTarget, ComponentTree)
cli.py ──> resolution.py (resolve_target)
validate_config.py ──> resolution.py (resolve_target)
discover_components.py ──> resolution.py (build_component_tree)
process.py ──> models.py (ComponentTree.all_source_dirs)
```

#### T-16: Create Section 4.5 Data Models

**Source**: Current Section 3.3 (ComponentTree), Section 3.5 (PortifyConfig changes), Section 3.6 (ValidateConfigResult changes). Move all Python dataclass definitions here.

This is the heaviest content move — ~200 lines of Python code from Section 3 to Section 4.5.

#### T-17: Create Section 4.6 Implementation Order

**Source**: Current Section 4.3 (Implementation Phases, lines 658-701)

Reformat from prose phases into the template's numbered list format with parallel annotations:

```
1. models.py (data models)                    -- no existing code changes
2. resolution.py (new module)                 -- [parallel with 1]
3. discover_components.py (discovery)         -- depends on 1, 2
4. process.py (subprocess scoping)            -- depends on 1
   validate_config.py (validation)            -- [parallel with 4]
5. cli.py + config.py (CLI wiring)            -- depends on 3, 4
6. Tests + fixtures                            -- depends on all above
```

---

### Phase 6: Section 5 — Interface Contracts (Tasks 18-20)

#### T-18: Create Section 5.1 CLI Surface

**Source**: Current Section 3.1.2 (CLI Interface Change, lines 79-116)

Reformat the Click code into the template's CLI Surface table:

```markdown
### 5.1 CLI Surface

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `TARGET` | STRING (argument) | required | Command name, path, skill directory, or skill name to portify |
| `--commands-dir` | PATH | auto-detect | Override commands directory |
| `--skills-dir` | PATH | auto-detect | Override skills directory |
| `--agents-dir` | PATH | auto-detect | Override agents directory |
| `--include-agent` | STRING (multiple) | none | Include additional agent(s) by name or path |
| `--save-manifest` | PATH | none | Save resolved component tree as manifest file |
| `--output` | PATH | auto | Output directory for generated artifacts |
| `--dry-run` | FLAG | false | Halt after Step 2 |
| `--skip-review` | FLAG | false | Skip interactive review gates |
| `--start` | STRING | none | Resume from specific step |
| ... | | | (existing options unchanged) |
```

#### T-19: Create Section 5.2 Gate Criteria

**Source**: No gate changes in this spec — gates are content-based, not input-based. State explicitly:

```markdown
### 5.2 Gate Criteria

Gate criteria are unchanged from v2.24. All existing gates (ANALYZE_WORKFLOW_GATE through PANEL_REVIEW_GATE) remain valid. The enriched `component-inventory.md` artifact provides more context to Claude subprocesses but does not alter gate evaluation logic.
```

#### T-20: Create Section 5.3 Phase Contracts

**Source**: No contract schema changes. State explicitly with reference to v2.24 contracts:

```markdown
### 5.3 Phase Contracts

Phase contract schema is unchanged from v2.24. The `PortifyContract` emitted by `contract.py` retains all existing fields. New fields in `ValidateConfigResult` (command_path, skill_dir, target_type, agent_count) are informational additions that do not alter contract structure.
```

---

### Phase 7: Section 6 — Non-Functional Requirements (Task 21)

#### T-21: Create Section 6 Non-Functional Requirements

**Source**: Extract from scattered mentions throughout current spec:
- Resolution <1s (Section 3.1.1)
- Backward compatibility requirement (Section 6)
- Zero base-module modifications (implied throughout)
- Directory cap at 10 (Section 3.4.3)

```markdown
## 6. Non-Functional Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| NFR-WORKFLOW.1 | Target resolution performance | <1s for all 6 input forms | `time.monotonic()` in `resolve_target()` |
| NFR-WORKFLOW.2 | Zero base-module modifications | 0 changes to `pipeline/` or `sprint/` | `git diff --name-only` |
| NFR-WORKFLOW.3 | Synchronous-only execution | No `async def` or `await` in new code | `grep -r "async def\|await"` |
| NFR-WORKFLOW.4 | Backward compatibility | All existing skill-dir inputs produce identical behavior | Existing test suite passes unchanged |
| NFR-WORKFLOW.5 | Subprocess directory cap | Warning at >10 `--add-dir` entries | Consolidation logic in `_build_add_dir_args()` |
```

---

### Phase 8: Sections 7-9 — Renumber Existing Sections (Tasks 22-24)

#### T-22: Renumber Risk Assessment from Section 8 to Section 7

Move current Section 8 content to Section 7 unchanged. Verify table format matches template (Risk | Probability | Impact | Mitigation).

#### T-23: Renumber Test Plan from Section 5 to Section 8

Move current Section 5 content to Section 8. Add explicit subsection numbers:
- `### 8.1 Unit Tests` — resolution tests, component tree tests, agent extraction tests
- `### 8.2 Integration Tests` — full resolution + discovery + subprocess scoping
- `### 8.3 Manual / E2E Tests` — run against real workflows (sc:roadmap, sc:cleanup-audit)

Create 8.3 Manual/E2E Tests from edge cases in current Section 7:

```markdown
### 8.3 Manual / E2E Tests

| Scenario | Steps | Expected Outcome |
|----------|-------|-----------------|
| Portify sc:roadmap by name | `superclaude cli-portify run roadmap --dry-run` | Resolves command + skill + agents; component-inventory.md has all tiers |
| Portify by skill dir (backward compat) | `superclaude cli-portify run src/.../sc-roadmap-protocol/` | Same result as name-based; command backward-resolved |
| Missing agent graceful degradation | Use skill referencing nonexistent agent | Warning emitted; pipeline continues with found=False agent |
| Manifest save | `superclaude cli-portify run roadmap --save-manifest ./manifest.md --dry-run` | manifest.md written with full tree |
```

#### T-24: Renumber Migration from Section 6 to Section 9

Move current Section 6 content to Section 9. Add template-required fields:

```markdown
- **Breaking changes**: No. The `TARGET` argument is a superset of the old `WORKFLOW_PATH`.
- **Backwards compatibility**: Existing skill-directory inputs resolve identically via backward-resolution. `resolve_workflow_path()` preserved unchanged.
- **Rollback plan**: Revert to v2.24 CLI argument (`WORKFLOW_PATH` with `type=click.Path(exists=True)`). No data model migration needed — new fields have defaults.
```

---

### Phase 9: Missing Sections (Tasks 25-27)

#### T-25: Create Section 10 Downstream Inputs

```markdown
## 10. Downstream Inputs

### For sc:roadmap
- **Themes**: "Workflow resolution", "Component tree discovery", "Subprocess scoping"
- **Milestones**: 7 implementation phases (data models → resolution → discovery → scoping → CLI → validation → tests)
- **Estimated tasks**: 15-20 tasks across 7 phases
- **Complexity class**: MODERATE (0.65)

### For sc:tasklist
- **Phase structure**: 7 phases with clear dependency ordering
- **Tier distribution**: Mix of STRICT (resolution correctness, subprocess scoping), STANDARD (discovery enrichment), EXEMPT (data model additions)
- **Deliverable count**: ~15 deliverables (1 new module, 6 modified modules, 1 fixture set, ~32 tests)
- **Parallelization**: Phases 1-2 (models + resolution) can run in parallel; Phase 3-4 (discovery + scoping) can run in parallel after 1-2 complete
```

#### T-26: Create Section 11 Open Items

**Source**: Current Section 10 (Open Questions, lines 888-897). Reformat to template table:

```markdown
## 11. Open Items

| Item | Question | Impact | Resolution Target |
|------|----------|--------|-------------------|
| OI-1 | Should agent-to-agent refs be recursively resolved? | Medium — some agents delegate to sub-agents | Deferred to v2.25. O(1)-depth in v2.24.1. |
| OI-2 | Should manifest loading be supported as input? | Low — save-manifest is write-only in v2.24.1 | Deferred to v2.25 if user demand exists. |
| OI-3 | Should `--exclude-component` be supported? | Low — not needed if discovery is accurate | Deferred to v2.25. |
| OI-4 | Quality scores for this spec | Required for release readiness | Run `/sc:spec-panel` after template alignment |
```

#### T-27: Create Section 12 Brainstorm Gap Analysis + Appendices

**Section 12**: Reference the adversarial brainstorm that produced this spec:

```markdown
## 12. Brainstorm Gap Analysis

Gap analysis was performed via structured adversarial debate between two competing approaches (Approach A: Command-Centric, Approach B: Manifest-Based). Three ideas from the losing approach were incorporated.

| Gap ID | Description | Severity | Affected Section | Persona |
|--------|-------------|----------|-----------------|---------|
| GAP-B1 | No debugging output for resolution logic | Medium | 5.1 CLI Surface | analyzer |
| GAP-B2 | Heuristic agent extraction may miss references | Medium | 3, FR-2 | qa |
| GAP-B3 | Enriched inventory aids Claude analysis quality | Low | FR-2 | architect |

**Resolution**: GAP-B1 addressed via `--save-manifest`. GAP-B2 addressed via `--include-agent`. GAP-B3 addressed via enriched `component-inventory.md`.
```

**Appendix A: Glossary**:

```markdown
## Appendix A: Glossary

| Term | Definition |
|------|-----------|
| Tier 0 | Command `.md` file — thin entry point that dispatches to a skill |
| Tier 1 | Skill/Protocol — full behavioral specification in a skill directory |
| Tier 2 | Refs, rules, templates, scripts — step-specific detail loaded on-demand |
| ComponentTree | In-memory hierarchical model of all workflow components |
| ResolvedTarget | Normalized result of input resolution — command path, skill dir, project root |
| Backward-resolution | Deriving the command file from a skill directory name |
| Manifest | Optional serialized representation of the ComponentTree for debugging |
```

**Appendix B: References**:

```markdown
## Appendix B: Reference Documents

| Document | Relevance |
|----------|-----------|
| `synthesized-spec.md` (this spec's source) | Pre-template-alignment version |
| `brainstorm-approach-a.md` | Winning approach (command-centric) |
| `brainstorm-approach-b.md` | Losing approach (manifest-based) — 3 ideas incorporated |
| `debate-transcript.md` | 3-round adversarial debate record |
| `scoring-matrix.md` | 6-criteria weighted scoring (A: 7.95, B: 7.00) |
| `context-overview.md` | Gap discovery documentation |
| `docs/architecture/command-skill-policy.md` | Tier 0/1/2 architecture definition |
| `.claude/skills/sc-cli-portify-protocol/refs/analysis-protocol.md` | Protocol-level discovery requirements |
| `src/superclaude/examples/release-spec-template.md` | Target template for this alignment |
```

**Source**: Footer lines 900-903 (synthesis provenance — base variant, date, orchestrator) route into this table as the first entry.

**Appendix C: Effort Estimate** (preserves current Section 9 content):

```markdown
## Appendix C: Effort Estimate

| Phase | Description | Files Changed | New Files | Estimated Effort |
|-------|-------------|--------------|-----------|-----------------|
| 1 | Data models | `models.py` | -- | 2-3 hours |
| 2 | Resolution algorithm | -- | `resolution.py` | 4-6 hours |
| 3 | Discovery integration | `discover_components.py` | -- | 3-4 hours |
| 4 | Subprocess scoping | `process.py` | -- | 1-2 hours |
| 5 | CLI update | `cli.py`, `config.py` | -- | 2-3 hours |
| 6 | Validation update | `validate_config.py` | -- | 2-3 hours |
| 7 | Tests | Multiple test files | `fixtures/mock_project/` | 5-7 hours |
| **Total** | | **6 files modified** | **1 new file + fixtures** | **19-28 hours** |

Estimated sessions: 2-3 focused implementation sessions.
```

**Source**: Current Section 9 lines 871-884 moved here verbatim.

---

## Content Movement Map

Shows where every piece of current spec content ends up in the aligned version.

| Current Location | Content Summary | New Location |
|---|---|---|
| Lines 1-8 (header) | Title, status, version, date, base, incorporated | T-01 → YAML frontmatter + T-02 title + Appendix B |
| Lines 11-22 (Section 1) | Problem statement + gap table | Section 1 (keep) + 1.1 Evidence (T-03) + 1.2 Scope (T-04) |
| Lines 25-58 (Section 2) | Solution overview + architecture + decisions | 2 (keep) + 2.1 Key Decisions table (T-06) + 2.2 Data Flow (T-07) |
| Lines 62-148 (Section 3.1) | Input model, CLI changes, normalization | FR-1 (T-09) + 5.1 CLI Surface (T-18) + 4.5 Data Models (T-16) |
| Lines 150-211 (Section 3.2) | Resolution algorithm (R1-R5) | FR-1 (T-09) + 4.5 Data Models (T-16) |
| Lines 212-439 (Section 3.3) | ComponentTree + all Python code | 4.5 Data Models (T-16) |
| Lines 441-509 (Section 3.4) | Subprocess scoping | FR-3 (T-11) + 4.5 Data Models (T-16) |
| Lines 511-560 (Section 3.5) | PortifyConfig changes | 4.5 Data Models (T-16) |
| Lines 562-602 (Section 3.6) | validate_config changes | FR-1 acceptance criteria + 4.2 Modified Files (T-13) |
| Lines 604-635 (Section 3.7) | discover_components changes | FR-2 (T-10) + 4.2 Modified Files (T-13) |
| Lines 631-636 (Section 3.8) | Manifest save (`--save-manifest` write-only semantics) | FR-2 acceptance criteria (T-10) + 5.1 CLI Surface (T-18) |
| Lines 639-701 (Section 4) | Implementation plan | 4.1 New Files (T-12) + 4.2 Modified (T-13) + 4.6 Order (T-17) |
| Lines 704-797 (Section 5) | Test plan + fixtures | 8. Test Plan (T-23) |
| Lines 801-823 (Section 6) | Migration | 9. Migration (T-24) |
| Lines 826-855 (Section 7) | Edge cases | 1.2 Scope Boundary (T-04) + 8.3 Manual Tests (T-23) + 11 Open Items (T-26) |
| Lines 858-868 (Section 8) | Risk assessment | 7. Risk Assessment (T-22) |
| Lines 871-884 (Section 9) | Effort estimate (phase table, hours, session count) | Appendix C: Effort Estimate (T-27) |
| Lines 900-903 (footer) | Synthesis provenance metadata | Appendix B: References (T-27) |
| Lines 888-897 (Section 10) | Open questions | 11. Open Items (T-26) |

**Verification**: Every line range in the current spec (including Section 3.8, Section 9 effort table, and footer metadata) maps to a target location. Zero content is deleted.

---

## Execution Notes for /sc:task-unified

- **Compliance tier**: STANDARD — single-file structural refactoring with no code changes
- **Strategy**: systematic — ordered phases with dependency tracking
- **Verification**: After all tasks complete, run `grep -c '{{SC_PLACEHOLDER:' output.md` to verify zero sentinels remain
- **Quality gate**: Run `/sc:spec-panel --focus correctness,architecture` after alignment to populate quality scores in frontmatter
