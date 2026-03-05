---
spec_source: ".dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md"
generated: "2026-03-05T01:40:00Z"
generator: sc:roadmap
complexity_score: 0.571
complexity_class: MEDIUM
domain_distribution:
  skill_generation: 32.5
  command_layer: 26.25
  tooling_devops: 22.5
  output_format: 10.0
  architecture_migration: 8.75
primary_persona: architect
consulting_personas: [analyzer, scribe]
milestone_count: 7
milestone_index:
  - id: M1
    title: "Foundation & Architecture Setup"
    type: FEATURE
    priority: P0
    dependencies: []
    deliverable_count: 4
    effort: S
    risk_level: Low
  - id: M2
    title: "Command Layer Implementation"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 8
    effort: M
    risk_level: Medium
  - id: M3
    title: "Skill Layer — v3.0 Repackaging"
    type: FEATURE
    priority: P0
    dependencies: [M1]
    deliverable_count: 8
    effort: L
    risk_level: High
  - id: V1
    title: "Integration Checkpoint"
    type: TEST
    priority: P2
    dependencies: [M2, M3]
    deliverable_count: 3
    effort: S
    risk_level: Low
  - id: M4
    title: "Tooling & Installation Integration"
    type: FEATURE
    priority: P1
    dependencies: [V1]
    deliverable_count: 5
    effort: M
    risk_level: Medium
  - id: M5
    title: "Output Validation & Sprint Compatibility"
    type: TEST
    priority: P1
    dependencies: [M4]
    deliverable_count: 6
    effort: M
    risk_level: Medium
  - id: V2
    title: "Final Acceptance Validation"
    type: TEST
    priority: P3
    dependencies: [M5]
    deliverable_count: 5
    effort: S
    risk_level: Low
total_deliverables: 39
total_risks: 11
estimated_phases: 4
validation_score: 0.908
validation_status: PASS
---

# Roadmap: `/sc:tasklist` Command + Skill v1.0

## Overview

This roadmap packages the existing Tasklist Generator v3.0 as a proper SuperClaude command/skill pair, achieving exact functional parity with no new features. The work is organized into 5 work milestones and 2 validation checkpoints, following a 1:2 interleave ratio appropriate for MEDIUM complexity (0.571).

The primary risk is algorithm drift during the v3.0-to-SKILL.md reformatting process (RISK-001). The milestone structure front-loads architecture setup (M1) to establish the file layout, then parallelizes command layer (M2) and skill layer (M3) work before integrating with existing tooling (M4) and validating Sprint CLI compatibility (M5).

Key constraint: this is a pure packaging exercise. The v3.0 generator algorithm is the source of truth and must be preserved verbatim. No behavioral changes, no new features, no modifications to existing lint rules or install tooling.

## Milestone Summary

| ID | Title | Type | Priority | Effort | Dependencies | Deliverables | Risk |
|----|-------|------|----------|--------|--------------|--------------|------|
| M1 | Foundation & Architecture Setup | FEATURE | P0 | S | None | 4 | Low |
| M2 | Command Layer Implementation | FEATURE | P0 | M | M1 | 8 | Medium |
| M3 | Skill Layer — v3.0 Repackaging | FEATURE | P0 | L | M1 | 8 | High |
| V1 | Integration Checkpoint | TEST | P2 | S | M2, M3 | 3 | Low |
| M4 | Tooling & Installation Integration | FEATURE | P1 | M | V1 | 6 | Medium |
| M5 | Output Validation & Sprint Compatibility | TEST | P1 | M | M4 | 5 | Medium |
| V2 | Final Acceptance Validation | TEST | P3 | S | M5 | 5 | Low |

## Dependency Graph

```
M1 → M2 ─┐
          ├→ V1 → M4 → M5 → V2
M1 → M3 ─┘
```

M2 and M3 are parallelizable after M1 completes. V1 gates all downstream work on both command and skill being present.

---

## M1: Foundation & Architecture Setup

### Objective

Establish the file layout, directory structure, and empty scaffolding for the `/sc:tasklist` command/skill pair per §4.1.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D1.1 | Create directory `src/superclaude/skills/sc-tasklist-protocol/` with subdirs `rules/` and `templates/` | Directories exist; `mkdir -p` creates full tree |
| D1.2 | Create empty `src/superclaude/skills/sc-tasklist-protocol/__init__.py` | File exists, zero bytes, satisfies Python packaging (FR-008, NFR-012) |
| D1.3 | Create placeholder `src/superclaude/commands/tasklist.md` with valid YAML frontmatter only | Frontmatter parses; `name: tasklist` present |
| D1.4 | Create placeholder `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` with valid frontmatter only | Frontmatter parses; `name: sc:tasklist-protocol` present |

### Dependencies

- None (first milestone)

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| `__init__.py` triggers unintended package discovery (RISK-009) | Low | Low | Verify `pyproject.toml` package discovery config excludes skill dirs from Python import scanning |

---

## M2: Command Layer Implementation

### Objective

Write the full `tasklist.md` command file with argument parsing, input validation, activation section, and boundaries per §5.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D2.1 | Implement YAML frontmatter per §5.1: name, description, category, complexity, allowed-tools, mcp-servers, personas, version | All 8 frontmatter fields present and matching spec values (FR-026–FR-030) |
| D2.2 | Implement all 8 required sections per §5.3: Triggers, Usage, Behavioral Summary, Arguments, Input Validation, Activation, Examples, Boundaries | All sections present with correct headings (FR-031) |
| D2.3 | Implement argument spec per §5.2: required `<roadmap-path>`, optional `--spec`, optional `--output` | Arguments table matches spec; `@file` and explicit path both work (FR-013–FR-016) |
| D2.4 | Implement input validation per §5.4: 4 validation checks + 2-field error format + exit-without-invoke behavior | All 4 checks documented; error format `error_code` + `message`; command exits on failure (FR-018–FR-022, NFR-013) |
| D2.5 | Implement `## Activation` section per §5.5: mandatory `Skill sc:tasklist-protocol` invocation | Activation section contains exact invocation text; context passing documented (FR-024) |
| D2.6 | Implement `## Boundaries` per §5.6: Will/Will-Not contract | Both lists present and match spec (FR-032, FR-033) |
| D2.7 | Emit STRICT tier classification header before skill invocation per §4.3 | Classification header present in command output before `Skill sc:tasklist-protocol` invocation (FR-023) |
| D2.8 | Report generated file paths on completion; implement TASKLIST_ROOT auto-derivation per §3.1 | File paths printed to stdout on success (FR-025); TASKLIST_ROOT derivation logic matches §3.1 algorithm when `--output` omitted (FR-017) |

### Dependencies

- M1: Directory structure and placeholder file exist

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Command file exceeds 200-line warning threshold (RISK-007) | Medium | Low | Use concise prose; 3-4 examples max; refer to skill for algorithm details instead of duplicating |
| Command file exceeds 500-line hard fail (RISK-007) | Low | High | If approaching 400 lines, audit for content that belongs in the skill |

---

## M3: Skill Layer — v3.0 Repackaging

### Objective

Reformat the v3.0 Tasklist Generator algorithm (`Tasklist-Generator-Prompt-v2.1-unified.md`) into `SKILL.md` format with extracted reference files, achieving exact functional parity.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D3.1 | Implement SKILL.md frontmatter per §6.1 | All fields present: `name: sc:tasklist-protocol`, description, category, complexity, allowed-tools, mcp-servers, personas; `name:` ends in `-protocol` (FR-053–FR-057) |
| D3.2 | Reformat v3.0 §0–§9 + Appendix into SKILL.md body per §6.2 structural mapping | Each v3.0 section maps to corresponding SKILL.md section; content is verbatim (FR-034, FR-035) |
| D3.3 | Add stage completion reporting contract (§4.3) to SKILL.md | 6 stages with validation criteria; TodoWrite integration; structural vs. semantic gate distinction (FR-036–FR-049) |
| D3.4 | Extract `rules/tier-classification.md` from SKILL.md §5.3 + Appendix | File exists; content matches §5.3 tier keywords, compound phrases, context boosters (FR-009) |
| D3.5 | Extract `rules/file-emission-rules.md` from SKILL.md §3.3 | File exists; content matches §3.3 naming conventions, heading format, content boundaries (FR-010) |
| D3.6 | Extract `templates/index-template.md` from SKILL.md §6A | File exists; content is the complete tasklist-index.md template (FR-011) |
| D3.7 | Extract `templates/phase-template.md` from SKILL.md §6B | File exists; content is the complete phase-N-tasklist.md template with task format, checkpoints (FR-012) |
| D3.8 | Document Tool Usage (§6.4) and MCP Usage (§6.5) sections in SKILL.md | SKILL.md contains explicit Tool Usage section mapping Read/Grep/Write/TodoWrite/Bash/Glob to phases (FR-060); MCP Usage section specifies sequential for tier classification (FR-058) and context7 for pattern validation (FR-059) |

### Dependencies

- M1: Directory structure exists for `sc-tasklist-protocol/`, `rules/`, `templates/`

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Algorithm drift during reformatting (RISK-001) | Medium | High | Diff v3.0 source against SKILL.md body after reformatting; any non-formatting delta is a defect |
| §3.1 TASKLIST_ROOT algorithm gap (RISK-002) | Medium | High | Locate the algorithm in the v3.0 source before starting; document the exact derivation logic |
| Pre-write quality gate definitions undefined (RISK-008) | High | Medium | Define pass/fail criteria for semantic and structural gates based on §9 AC #8 and #9; document in SKILL.md |

---

## V1: Integration Checkpoint

### Objective

Validate that the command and skill pair integrate correctly: the command invokes the skill, the skill's structure is valid, and the pair passes basic lint checks.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV1.1 | Verify command `## Activation` correctly references `sc:tasklist-protocol` and skill directory exists | Lint check #1 passes: `## Activation` → `sc-tasklist-protocol/` exists (FR-071) |
| DV1.2 | Verify bidirectional pairing: skill dir exists → command file exists | Lint check #2 passes (FR-072) |
| DV1.3 | Verify SKILL.md frontmatter passes lint checks #8 and #9 | `name:`, `description:`, `allowed-tools:` present; `name:` ends in `-protocol` (FR-076, FR-057) |

### Dependencies

- M2: `tasklist.md` fully implemented
- M3: `SKILL.md` fully implemented with all reference files

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| lint-architecture rule incompatibility (RISK-003) | Low | High | Run `make lint-architecture` early in milestone; if unknown edge case, investigate rule source before modifying anything |

---

## M4: Tooling & Installation Integration

### Objective

Ensure the command/skill pair integrates with `superclaude install`, `make sync-dev`, `make verify-sync`, and `make lint-architecture` tooling.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D4.1 | `make sync-dev` copies `commands/tasklist.md` to `.claude/commands/sc/` and `skills/sc-tasklist-protocol/` to `.claude/skills/` | Files exist in `.claude/` after sync (FR-069) |
| D4.2 | `make verify-sync` confirms both source and `.claude/` copies are identical | No diff between `src/superclaude/` and `.claude/` copies (FR-070) |
| D4.3 | `make lint-architecture` passes with zero errors for the new pair | All 6 lint checks pass (FR-003, FR-071–FR-076, NFR-007) |
| D4.4 | `superclaude install` installs `tasklist.md` to `~/.claude/commands/sc/tasklist.md` | File exists at install target after `superclaude install` (FR-067) |
| D4.5 | `superclaude install` does NOT install `sc-tasklist-protocol/` to `~/.claude/skills/` | Skill directory absent from `~/.claude/skills/` (FR-068, NFR-006, NFR-010) |
| D4.6 | Verify source files unmodified after all work completes | `git diff` confirms v3.0 generator prompt (`Tasklist-Generator-Prompt-v2.1-unified.md`) and `TasklistGenPrompt.md` are unchanged (FR-079, FR-080) |

### Dependencies

- V1: Integration checkpoint passed; command/skill pair structurally valid

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Skill install isolation failure (RISK-005) | Low | Medium | Verify `_has_corresponding_command` logic in installer handles `sc-tasklist-protocol` correctly |
| lint-architecture rule edge cases (RISK-003) | Low | High | If lint fails on the new pair, investigate the specific failing check before any modifications |
| Command line count creep (RISK-007) | Medium | Low | Measure line count after M2; if >200, trim before running lint |

---

## M5: Output Validation & Sprint Compatibility

### Objective

Validate that the generated tasklist bundles are correct, lean, Sprint CLI-compatible, and functionally identical to the v3.0 generator output.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| D5.1 | Manual test: `/sc:tasklist @<roadmap>` produces valid `tasklist-index.md` + `phase-N-tasklist.md` files | Index has Phase Files table with literal filenames; phase files exist on disk (FR-061, FR-044, FR-045) |
| D5.2 | Sprint compatibility test: `superclaude sprint run <generated-index>` discovers all phase files | Sprint CLI finds and lists all phase files from the generated index (FR-066, FR-078) |
| D5.3 | Functional parity test: diff v3.0 generator output vs. `/sc:tasklist` output on same roadmap input | Output is structurally identical; any delta is non-functional formatting only (FR-005, NFR-002) |
| D5.4 | Leanness check: phase files contain no registries, traceability matrices, or embedded templates | Phase files contain only task content per Sprint format (FR-064, NFR-008) |
| D5.5 | Task description quality: every task description is standalone (names artifact, uses concrete verb, no external refs) | Spot-check 100% of tasks against §9 AC #11 criteria (FR-065, NFR-009) |

### Dependencies

- M4: Tooling integration complete; install and lint passing

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Sprint CLI naming convention mismatch (RISK-004) | Medium | High | Run `superclaude sprint run` early; verify the exact filename pattern it expects via source code inspection |
| Algorithm drift producing non-identical output (RISK-001) | Medium | High | Use canonical test roadmap; diff outputs character-by-character |
| Task ID collision on large roadmap (RISK-010) | Low | Medium | Test with a roadmap producing >10 phases to verify `T<PP>.<TT>` range |

---

## V2: Final Acceptance Validation

### Objective

Verify all 13 success criteria (SC-001 through SC-013) pass and the implementation meets all acceptance criteria from §9.

### Deliverables

| ID | Description | Acceptance Criteria |
|----|-------------|---------------------|
| DV2.1 | SC-001 through SC-005 verified: discoverability, output format, lint | All 5 criteria pass (SC-001–SC-005) |
| DV2.2 | SC-006 through SC-009 verified: Sprint compatibility, lean output, stage order, v3.0 parity | All 4 criteria pass (SC-006–SC-009) |
| DV2.3 | SC-010 through SC-012 verified: quality gates, atomic output | Pre-write gates enforced; no files on Stage 1–4 failure (SC-010–SC-012) |
| DV2.4 | SC-013 verified: task descriptions standalone | Every task passes standalone check (SC-013) |
| DV2.5 | Verify manual TasklistGenPrompt.md workflow is superseded | `/sc:tasklist` provides equivalent functionality; internal docs updated to reference `/sc:tasklist` (FR-004) |

### Dependencies

- M5: Output validation complete

### Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Pre-write quality gate criteria still undefined (RISK-008) | High | Medium | Must be resolved in M3; V2 validates the criteria are defined and enforced |

---

## Risk Register

| ID | Risk | Affected Milestones | Probability | Impact | Mitigation | Owner |
|----|------|---------------------|-------------|--------|------------|-------|
| R-001 | Algorithm drift during v3.0→SKILL.md reformatting | M3, M5, V2 | Medium | High | Character-level diff of v3.0 source vs. SKILL.md body; flag any non-formatting delta | architect |
| R-002 | §3.1 TASKLIST_ROOT derivation algorithm is defined in v3.0 source, not this spec | M3 | Medium | High | Locate and document the exact algorithm from v3.0 before starting M3 | architect |
| R-003 | Existing lint-architecture rules may have edge cases rejecting the new pair | V1, M4 | Low | High | Run lint early; investigate rule source before any modifications (NFR-007 prohibits rule changes) | analyzer |
| R-004 | Sprint CLI naming convention (`phase-N-tasklist.md`) not fully specified | M5 | Medium | High | Inspect `superclaude sprint run` source code for expected filename pattern | architect |
| R-005 | Skill install isolation failure (`_has_corresponding_command` edge case) | M4 | Low | Medium | Verify installer logic handles `sc-tasklist-protocol` → `tasklist.md` pairing correctly | analyzer |
| R-006 | MCP servers (`sequential`, `context7`) unavailable at runtime | M5, V2 | Medium | Medium | Document MCP as optional for tier classification; core generation works without MCP | architect |
| R-007 | Command file (`tasklist.md`) exceeds line count limits | M2, M4 | Medium | Low | Target <150 lines; audit content that should live in skill instead | architect |
| R-008 | Pre-write semantic/structural quality gate criteria undefined in spec | M3, V2 | High | Medium | Define explicit pass/fail criteria in SKILL.md based on §9 AC #8 and #9 | architect |
| R-009 | `__init__.py` triggers unintended Python package discovery | M1 | Low | Low | Verify `pyproject.toml` excludes `skills/` from package scanning | analyzer |
| R-010 | Task ID `T<PP>.<TT>` collision in large roadmaps (>99 phases or tasks) | M5 | Low | Medium | Test with large roadmap input; verify ID scheme handles edge cases | analyzer |
| R-011 | Partial file write on mid-emission failure breaks atomicity guarantee | M3, M5 | Low | High | SKILL.md must validate all data in-memory before any Write() call; Stage 5 is all-or-nothing | architect |

## Decision Summary

| Decision | Chosen | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Primary Persona | architect | analyzer (0.273), scribe (0.12) | Highest domain coverage across Skill/Generation (32.5%) and Architecture (8.75%) domains |
| Template | inline | No local/user/plugin templates found | 4-tier discovery produced zero candidates; fallback to inline generation |
| Milestone Count | 7 (5 work + 2 validation) | Range 5-7 (MEDIUM class) | Formula: base(5) + floor(3 domains / 2) = 6 work → +2 validation at 1:2 ratio = 7 total; adjusted to 5 work + 2 validation for cleaner interleaving |
| Adversarial Mode | none | N/A | No `--multi-roadmap` or `--specs` flags provided |
| Compliance Tier | STRICT | STANDARD (auto-detect) | User-specified `--compliance strict`; complexity 0.571 would auto-detect as STANDARD |
| M2/M3 Parallelization | Parallel after M1 | Sequential (M2 → M3) | Command and skill have no mutual dependencies until integration (V1); parallel reduces critical path |

## Success Criteria

| ID | Criterion | Validates Milestone(s) | Measurable |
|----|-----------|----------------------|------------|
| SC-001 | `/sc:tasklist` discoverable in Claude Code command palette | M4 (install) | Yes |
| SC-002 | Output `tasklist-index.md` has Phase Files table with literal filenames | M5 (output) | Yes |
| SC-003 | Output `phase-N-tasklist.md` files match Sprint CLI naming | M5 (output) | Yes |
| SC-004 | All tasks have `T<PP>.<TT>` IDs, tier classifications, metadata | M3, M5 | Yes |
| SC-005 | `make lint-architecture` passes with zero errors | V1, M4 | Yes |
| SC-006 | `superclaude sprint run` discovers all phase files | M5 | Yes |
| SC-007 | Phase files are lean (no registries/matrices/templates) | M5 | Yes |
| SC-008 | Stages execute in order 1–6 with TodoWrite reporting | M3 | Yes |
| SC-009 | Output identical to v3.0 generator on same input | M5 | Yes (diff) |
| SC-010 | Pre-write semantic quality gate passes | M3, V2 | Yes |
| SC-011 | Pre-write structural quality gate passes | M3, V2 | Yes |
| SC-012 | No output files written if Stage 1–4 validation fails | M3, V2 | Yes |
| SC-013 | Every task description is standalone | M5, V2 | Yes |
