---
spec_source: ".dev/releases/current/v2.07-tasklist-v1/sc-tasklist-command-spec-v1.0.md"
generated: "2026-03-05T01:40:00Z"
generator: sc:roadmap
functional_requirements: 80
nonfunctional_requirements: 15
total_requirements: 95
domains_detected: [skill_generation, command_layer, tooling_devops, output_format, architecture_migration]
complexity_score: 0.571
complexity_class: MEDIUM
risks_identified: 11
dependencies_identified: 12
success_criteria_count: 13
extraction_mode: standard
---

# Extraction Report: `/sc:tasklist` Command + Skill v1.0

**Source**: `sc-tasklist-command-spec-v1.0.md`
**Extraction Date**: 2026-03-05

## Project Summary

Package the existing Tasklist Generator v3.0 as a proper SuperClaude command/skill pair (`/sc:tasklist`), making it discoverable via the Claude Code command palette, installable via `superclaude install`, and lint-validated via `make lint-architecture` — achieving exact functional parity with the current v3.0 generator with no new features.

## Domain Analysis

| Domain | Percentage | Key Areas |
|--------|-----------|-----------|
| Skill / Generation | 32.5% | SKILL.md content, 6-stage pipeline, stage validations, tool/MCP usage |
| Command Layer | 26.25% | Argument parsing, input validation, frontmatter, sections, boundaries |
| Tooling / DevOps | 22.5% | Install, lint-architecture, sync-dev, verify-sync, CLI integration |
| Output / Format | 10.0% | Generated file structure, naming conventions, task metadata, leanness |
| Architecture / Migration | 8.75% | File layout, extracted reference files, non-modification rules |

## Functional Requirements (FRs)

### Core Goals (FR-001 – FR-005)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-001 | `/sc:tasklist` must be discoverable via the Claude Code command palette | P0 | §2 Goal #1 |
| FR-002 | Command/skill pair must install via `superclaude install` | P0 | §2 Goal #2 |
| FR-003 | Command/skill pair must pass `make lint-architecture` with no errors | P0 | §2 Goal #3 |
| FR-004 | Must replace the manual `TasklistGenPrompt.md` workflow | P0 | §2 Goal #4 |
| FR-005 | Output must be functionally identical to running v3.0 generator manually | P0 | §2 Goal #5 |

### Architecture (FR-006 – FR-012)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-006 | Command file placed at `src/superclaude/commands/tasklist.md` | P0 | §4.1, §8.1 |
| FR-007 | Skill file placed at `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` | P0 | §4.1, §8.1 |
| FR-008 | Empty `__init__.py` for Python packaging | P0 | §4.1, §8.1 |
| FR-009 | `rules/tier-classification.md` extracted from SKILL.md §5.3 + Appendix | P1 | §4.1, §6.3 |
| FR-010 | `rules/file-emission-rules.md` extracted from SKILL.md §3.3 | P1 | §4.1, §6.3 |
| FR-011 | `templates/index-template.md` extracted from SKILL.md §6A | P1 | §4.1, §6.3 |
| FR-012 | `templates/phase-template.md` extracted from SKILL.md §6B | P1 | §4.1, §6.3 |

### Command Layer (FR-013 – FR-033)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-013 | Parse arguments: `<roadmap-path>`, `--spec`, `--output` | P0 | §4.3, §5.2 |
| FR-014 | `<roadmap-path>` is required | P0 | §5.2 |
| FR-015 | `--spec <spec-path>` is optional | P1 | §5.2 |
| FR-016 | `--output <output-dir>` is optional | P1 | §5.2 |
| FR-017 | Auto-derive `TASKLIST_ROOT` from roadmap content when `--output` not provided | P0 | §5.4 |
| FR-018 | Validate: `<roadmap-path>` resolves to readable, non-empty file | P0 | §5.4 |
| FR-019 | Validate: `--spec` path resolves to readable file if provided | P0 | §5.4 |
| FR-020 | Validate: `--output` parent directory exists if provided | P0 | §5.4 |
| FR-021 | On validation failure: emit 2-field error (`error_code` + `message`) to stderr | P0 | §5.4 |
| FR-022 | On validation failure: exit without invoking skill | P0 | §5.4 |
| FR-023 | Emit STRICT tier classification header | P0 | §4.3 |
| FR-024 | `## Activation` section must contain `Skill sc:tasklist-protocol` invocation | P0 | §5.5 |
| FR-025 | Report generated file paths upon completion | P1 | §5.6 |
| FR-026 | Frontmatter: `name: tasklist`, `category: utility`, `complexity: high` | P0 | §5.1 |
| FR-027 | Frontmatter: `allowed-tools: Read, Glob, Grep, Write, Bash, TodoWrite, Skill` | P0 | §5.1 |
| FR-028 | Frontmatter: `mcp-servers: [sequential, context7]` | P0 | §5.1 |
| FR-029 | Frontmatter: `personas: [analyzer, architect]` | P0 | §5.1 |
| FR-030 | Frontmatter: `version: "1.0.0"` | P0 | §5.1 |
| FR-031 | Required sections: Triggers, Usage, Behavioral Summary, Arguments, Input Validation, Activation, Examples, Boundaries | P0 | §5.3 |
| FR-032 | Boundaries `Will do`: parse/validate args, derive TASKLIST_ROOT, invoke skill, report paths | P0 | §5.6 |
| FR-033 | Boundaries `Will Not`: execute algorithm, modify roadmaps, run sprint, generate beyond bundle | P0 | §5.6 |

### Skill Layer (FR-034 – FR-060)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-034 | SKILL.md contains full v3.0 generator (§0–§9 + Appendix) in skill format | P0 | §6.2 |
| FR-035 | Structural mapping preserves v3.0 sections verbatim | P0 | §6.2 |
| FR-036 | Stage 1: Read roadmap text; read spec/context if provided | P0 | §4.3 |
| FR-037 | Stage 1 validation: roadmap non-empty, required sections present | P0 | §6.2 |
| FR-038 | Stage 2: Parse roadmap items; assign to phase buckets | P0 | §4.3 |
| FR-039 | Stage 2 validation: every item in exactly one phase; phase count ≥ 1 | P0 | §6.2 |
| FR-040 | Stage 3: Convert phase items to task format | P0 | §4.3 |
| FR-041 | Stage 3 validation: all items converted; `T<PP>.<TT>` IDs, no collisions | P0 | §6.2 |
| FR-042 | Stage 4: Assign Effort, Risk, Tier, Confidence to each task | P0 | §4.3 |
| FR-043 | Stage 4 validation: all tasks have Effort, Risk, Tier, Confidence | P0 | §6.2 |
| FR-044 | Stage 5: Write `tasklist-index.md` and `phase-N-tasklist.md` per phase | P0 | §4.3 |
| FR-045 | Stage 5 validation: all phase files referenced in index exist on disk | P0 | §6.2 |
| FR-046 | Stage 6: Run Sprint Compatibility Self-Check | P0 | §4.3 |
| FR-047 | Stage 6 validation: all assertions pass | P0 | §6.2 |
| FR-048 | Stages execute in strict order: 1 → 2 → 3 → 4 → 5 → 6 | P0 | §9 AC #6 |
| FR-049 | TodoWrite reports progress at each stage completion | P0 | §6.4 |
| FR-050 | No output files written unless Stages 1–4 pass | P0 | §9 AC #10 |
| FR-051 | Pre-write semantic quality gate must pass before file emission | P0 | §9 AC #8 |
| FR-052 | Pre-write structural quality gate must pass before file emission | P0 | §9 AC #9 |
| FR-053 | SKILL.md frontmatter: `name: sc:tasklist-protocol` | P0 | §6.1 |
| FR-054 | SKILL.md frontmatter: `description`, `category: utility`, `complexity: high` | P0 | §6.1 |
| FR-055 | SKILL.md frontmatter: `allowed-tools: Read, Glob, Grep, Write, Bash, TodoWrite` | P0 | §6.1 |
| FR-056 | SKILL.md frontmatter: `mcp-servers: [sequential, context7]` | P0 | §6.1 |
| FR-057 | SKILL.md `name:` field ends in `-protocol` | P0 | §7.3 |
| FR-058 | Use `sequential` MCP for tier classification reasoning | P1 | §6.5 |
| FR-059 | Use `context7` MCP for framework pattern validation | P1 | §6.5 |
| FR-060 | Tool usage: Read (input), Grep (parsing), Write (output), TodoWrite (tracking), Bash (mkdir), Glob (verify) | P0 | §6.4 |

### Output Requirements (FR-061 – FR-066)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-061 | `tasklist-index.md` has Phase Files table with literal filenames | P0 | §9 AC #2 |
| FR-062 | `phase-N-tasklist.md` files match Sprint CLI naming convention | P0 | §9 AC #2 |
| FR-063 | All tasks have `T<PP>.<TT>` IDs, tier classifications, per-task metadata | P0 | §9 AC #2 |
| FR-064 | Phase files are lean: no registries, traceability matrix, templates | P0 | §9 AC #5 |
| FR-065 | Every task description is standalone (self-contained, no external refs) | P0 | §9 AC #11 |
| FR-066 | `superclaude sprint run` can discover all phase files from generated index | P0 | §9 AC #4 |

### Tooling & Installation (FR-067 – FR-080)

| ID | Description | Priority | Source |
|---|---|---|---|
| FR-067 | `superclaude install` → `tasklist.md` at `~/.claude/commands/sc/tasklist.md` | P0 | §7.1 |
| FR-068 | `sc-tasklist-protocol/` NOT copied to `~/.claude/skills/` | P0 | §7.1 |
| FR-069 | `make sync-dev` works for this pair | P0 | §7.2 |
| FR-070 | `make verify-sync` passes for this pair | P0 | §7.2 |
| FR-071 | Lint: `## Activation` in command → skill directory exists | P0 | §7.3 |
| FR-072 | Lint: skill directory exists → command file exists | P0 | §7.3 |
| FR-073 | Lint: warn at 200 lines in command file | P1 | §7.3 |
| FR-074 | Lint: fail at 500 lines in command file | P0 | §7.3 |
| FR-075 | Lint: command has `## Activation` section | P0 | §7.3 |
| FR-076 | Lint: SKILL.md has `name:`, `description:`, `allowed-tools:` | P0 | §7.3 |
| FR-077 | Manual validation: `/sc:tasklist @<roadmap>` produces valid bundle | P0 | §8.3 |
| FR-078 | Sprint validation: `sprint run <index>` discovers all phases | P0 | §8.3 |
| FR-079 | Source v3.0 generator prompt NOT modified | P0 | §8.2 |
| FR-080 | `TasklistGenPrompt.md` NOT modified | P1 | §8.2 |

## Non-Functional Requirements (NFRs)

| ID | Description | Category | Constraint |
|---|---|---|---|
| NFR-001 | Command file within lint line limits | Maintainability | Warn ≥200, fail ≥500 |
| NFR-002 | SKILL.md functionally identical to v3.0 | Reliability | Zero behavioral drift |
| NFR-003 | Command layer contains no generation logic | Maintainability | 100% delegation to skill |
| NFR-004 | Task IDs unique with no collisions | Reliability | Zero collision tolerance |
| NFR-005 | Atomic output: no files if Stage 1–4 fails | Reliability | All-or-nothing emission |
| NFR-006 | Skill accessed only via paired command | Architecture | No direct user invocation |
| NFR-007 | Lint rules not modified | Maintainability | Zero lint rule changes |
| NFR-008 | Phase files lean (no extraneous content) | Maintainability | No registries/matrices/templates |
| NFR-009 | Task descriptions standalone | Usability | No external context needed |
| NFR-010 | Skill dir not installed globally | Architecture | Paired-access only |
| NFR-011 | Strict stage order (1–6) | Reliability | No skip/reorder |
| NFR-012 | `__init__.py` empty | Maintainability | Zero content |
| NFR-013 | Validation errors: 2-field format | Usability | `error_code` + `message` |
| NFR-014 | Phase Files table uses literal filenames | Reliability | No variables/templates |
| NFR-015 | Sprint CLI compatibility guaranteed | Compatibility | No modifications needed |

## Dependencies

| ID | Description | Type | Affected |
|---|---|---|---|
| DEP-001 | v3.0 Tasklist Generator algorithm (source for SKILL.md) | Internal | FR-034–FR-047 |
| DEP-002 | `TasklistGenPrompt.md` (historical reference, unmodified) | Internal | FR-080 |
| DEP-003 | `superclaude install` CLI (must support pair layout) | Internal | FR-002, FR-067, FR-068 |
| DEP-004 | `make lint-architecture` tooling (compatible without rule changes) | Internal | FR-003, FR-071–FR-076 |
| DEP-005 | `make sync-dev` / `make verify-sync` (handle new pair) | Internal | FR-069, FR-070 |
| DEP-006 | `superclaude sprint run` (consumes generated index) | Internal | FR-066, FR-078 |
| DEP-007 | `sequential` MCP server (runtime dependency) | External | FR-058 |
| DEP-008 | `context7` MCP server (runtime dependency) | External | FR-059 |
| DEP-009 | Claude Code slash command system (recognizes installed commands) | External | FR-001, FR-067 |
| DEP-010 | Python packaging / hatchling (package discovery) | Internal | FR-008 |
| DEP-011 | Sprint CLI naming convention (phase file format) | Internal | FR-062, FR-066 |
| DEP-012 | §3.1 TASKLIST_ROOT derivation algorithm (defined in v3.0) | Internal | FR-017 |

## Success Criteria

| ID | Description | Derived From | Measurable |
|---|---|---|---|
| SC-001 | Discoverable in Claude Code command palette | FR-001 | Yes |
| SC-002 | Produces `tasklist-index.md` with literal Phase Files table | FR-044, FR-061 | Yes |
| SC-003 | Produces `phase-N-tasklist.md` matching Sprint CLI naming | FR-044, FR-062 | Yes |
| SC-004 | All tasks have `T<PP>.<TT>` IDs, tier, metadata | FR-042, FR-063 | Yes |
| SC-005 | `make lint-architecture` passes with zero errors | FR-003 | Yes |
| SC-006 | `superclaude sprint run` discovers all phases | FR-066 | Yes |
| SC-007 | Phase files lean (no extraneous content) | FR-064 | Yes |
| SC-008 | Stages execute in order 1–6 with TodoWrite reporting | FR-048, FR-049 | Yes |
| SC-009 | Output identical to v3.0 generator | FR-005 | Yes (diff) |
| SC-010 | Pre-write semantic quality gate passes | FR-051 | Yes |
| SC-011 | Pre-write structural quality gate passes | FR-052 | Yes |
| SC-012 | No output if Stage 1–4 validation fails | FR-050 | Yes |
| SC-013 | Task descriptions standalone | FR-065 | Yes |

## Risks

| ID | Description | Probability | Impact | Affected |
|---|---|---|---|---|
| RISK-001 | Algorithm drift during v3.0→SKILL.md reformatting | Medium | High | FR-005, NFR-002 |
| RISK-002 | §3.1 TASKLIST_ROOT algorithm gap (defined in v3.0, not this spec) | Medium | High | FR-017 |
| RISK-003 | lint-architecture rule incompatibility | Low | High | FR-003, NFR-007 |
| RISK-004 | Sprint CLI naming convention ambiguity | Medium | High | FR-062, FR-066 |
| RISK-005 | Skill install isolation failure | Low | Medium | FR-068, NFR-006 |
| RISK-006 | MCP server unavailability at runtime | Medium | Medium | FR-058, FR-059 |
| RISK-007 | Command file line count creep | Medium | Low | FR-073, FR-074 |
| RISK-008 | Pre-write quality gate definition gap (criteria undefined) | High | Medium | FR-051, FR-052 |
| RISK-009 | `__init__.py` / package discovery interaction | Low | Low | FR-008 |
| RISK-010 | Task ID collision in large roadmaps | Low | Medium | FR-041 |
| RISK-011 | Partial file write on mid-emission failure | Low | High | FR-050, NFR-005 |

## Complexity Score Breakdown

| Factor | Raw | Normalized | Weight | Weighted |
|--------|-----|-----------|--------|----------|
| requirement_count | 95 (80 FR + 15 NFR) | 1.000 | 0.25 | 0.250 |
| dependency_depth | 3 | 0.375 | 0.25 | 0.094 |
| domain_spread | 3 (≥10% domains) | 0.600 | 0.20 | 0.120 |
| risk_severity | 1.64 weighted avg | 0.320 | 0.15 | 0.048 |
| scope_size | 393 lines | 0.393 | 0.15 | 0.059 |
| **Total** | | | | **0.571** |

**Classification**: MEDIUM → 5-7 milestones, 1:2 interleave ratio
