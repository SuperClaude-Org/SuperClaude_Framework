# PRD: `/sc:tasklist` Command + Skill v1.0

**Date**: 2026-03-04
**Status**: Draft
**Scope**: v1.0 parity — package existing Tasklist Generator v3.0 as a proper command/skill pair

---

## 1. Problem Statement

The Tasklist Generator exists as two loose prompt files:
- `TasklistGenPrompt.md` — a wrapper prompt with placeholder variables (`{RELEASE}`, `{RELEASEROADMAP}`, etc.)
- `Tasklist-Generator-Prompt-v2.1-unified.md` — the full generator algorithm (recently refactored to v3.0)

These are not integrated into the SuperClaude command/skill system. Users must manually locate, read, and fill in the wrapper prompt. There is no discoverability via `/sc:`, no install support, and no lint-architecture validation.

## 2. Goal

Package the Tasklist Generator as `/sc:tasklist` — a standard command + skill pair that:
1. Is discoverable via `/sc:tasklist` in Claude Code
2. Installs via `superclaude install` alongside all other commands
3. Passes `make lint-architecture` validation
4. Replaces the manual `TasklistGenPrompt.md` workflow
5. Achieves **exact functional parity** with the current v3.0 generator — no new features

## 3. Non-Goals (v1.0)

- No new generator features beyond what v3.0 already does
- No interactive mode or progressive generation
- No integration with `superclaude sprint run` (the *output* is compatible; the *invocation* is manual)
- No MCP-driven roadmap fetching or auto-detection
- No Python CLI integration (this is a command/skill pair, not a Click subcommand)

---

## 4. Architecture

### 4.1 File Layout

```
src/superclaude/
  commands/
    tasklist.md                          # Command file (user-invocable)
  skills/
    sc-tasklist-protocol/
      SKILL.md                           # Full v3.0 generator algorithm
      __init__.py                        # Empty (Python packaging)
      rules/
        tier-classification.md           # Extracted: §5.3 + Appendix tier rules
        file-emission-rules.md           # Extracted: §3.3 file emission rules
      templates/
        index-template.md               # Extracted: §6A index file template
        phase-template.md               # Extracted: §6B phase file template
```

### 4.2 Component Roles

| Component | Role | Content Source |
|-----------|------|---------------|
| `tasklist.md` | User-facing command. Parses arguments, validates inputs, invokes skill. | New (based on `TasklistGenPrompt.md`) |
| `SKILL.md` | Full generator protocol. The v3.0 algorithm in skill format. | `Tasklist-Generator-Prompt-v2.1-unified.md` (v3.0) |
| `rules/tier-classification.md` | Reference: tier keywords, compound phrases, context boosters | Extracted from SKILL.md §5.3 + Appendix |
| `rules/file-emission-rules.md` | Reference: naming conventions, heading format, content boundaries | Extracted from SKILL.md §3.3 |
| `templates/index-template.md` | Reference: tasklist-index.md structure | Extracted from SKILL.md §6A |
| `templates/phase-template.md` | Reference: phase-N-tasklist.md structure | Extracted from SKILL.md §6B |

### 4.3 Invocation Flow

```
User types: /sc:tasklist @roadmap.md --output .dev/releases/current/v2.1/
    │
    ▼
tasklist.md (command):
    1. Parse arguments: roadmap path, optional spec path, output directory
    2. Validate: roadmap file exists, output directory writable
    3. Emit classification header (STRICT — multi-file generation)
    4. Invoke: Skill sc:tasklist-protocol
    │
    ▼
sc-tasklist-protocol/SKILL.md (skill) — Stage Completion Reporting Contract:

  Stage 1: Input Ingest
    - Read roadmap text (§2 Input Contract)
    - Read spec/context if provided
    Validation: roadmap text is non-empty; required sections present

  Stage 2: Parse + Phase Bucketing
    - Parse roadmap items (§4.1)
    - Assign items to phase buckets (§4.2-4.3)
    Validation: all items assigned to exactly one phase; no items dropped

  Stage 3: Task Conversion
    - Convert phase items to task format (§4.4-4.5)
    Validation: all items produce valid task stubs with T<PP>.<TT> IDs; no ID collisions

  Stage 4: Enrichment
    - Assign effort/risk/tier/confidence to each task (§5)
    Validation: all tasks have non-empty effort, risk, tier, confidence fields

  Stage 5: File Emission
    - Write tasklist-index.md (§6A)
    - Write phase-N-tasklist.md per phase (§6B)
    Validation: all declared phase files exist on disk; index Phase Files table matches actual filenames

  Stage 6: Self-Check
    - Run Sprint Compatibility Self-Check (§8)
    Validation: all §8 checks pass; no check failures

  Stage reporting: Report completed stages in order using TodoWrite as each
  stage passes. Stage reporting is observational (debugging/progress tracking).

  Structural gates: For deterministic, structurally verifiable properties
  (non-empty output, valid ID format, field presence), the skill checks
  minimal viability before advancing. For semantic properties (content
  quality, prose adequacy), validation is advisory — logged but not blocking.
```

---

## 5. Command Specification (`tasklist.md`)

### 5.1 Frontmatter

```yaml
---
name: tasklist
description: "Generate deterministic, Sprint CLI-compatible tasklist bundles from roadmaps"
category: utility
complexity: high
allowed-tools: Read, Glob, Grep, Write, Bash, TodoWrite, Skill
mcp-servers: [sequential, context7]
personas: [analyzer, architect]
version: "1.0.0"
---
```

### 5.2 Arguments

```
/sc:tasklist <roadmap-path> [--spec <spec-path>] [--output <output-dir>]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<roadmap-path>` | Yes | — | Path to roadmap file (passed as `@file` reference) |
| `--spec <spec-path>` | No | — | Supplementary spec/context file |
| `--output <output-dir>` | No | Auto-derived from roadmap `TASKLIST_ROOT` | Output directory for the tasklist bundle |

### 5.3 Sections

| Section | Content |
|---------|---------|
| `# /sc:tasklist` | Title and one-line description |
| `## Triggers` | Roadmap-to-tasklist conversion requests, sprint planning |
| `## Usage` | Syntax, arguments, flags |
| `## Behavioral Summary` | Brief: "Transforms a roadmap into a Sprint CLI-compatible multi-file tasklist bundle" |
| `## Arguments` | Table of arguments with defaults |
| `## Input Validation` | Checks: roadmap exists, output dir writable, spec exists if provided |
| `## Activation` | **MANDATORY** skill invocation: `Skill sc:tasklist-protocol` |
| `## Examples` | 3-4 usage examples |
| `## Boundaries` | Will/Will Not contract |

### 5.4 Input Validation (Command Layer)

Before invoking the skill, the command validates:

1. `<roadmap-path>` resolves to a readable, non-empty file (reject 0-byte or whitespace-only files)
2. If `--spec` provided, it resolves to a readable file
3. If `--output` provided, the parent directory exists
4. If `--output` not provided, derive `TASKLIST_ROOT` from roadmap content using the §3.1 algorithm

On validation failure, emit a 2-field error to stderr:

    error_code: <category string, e.g., "EMPTY_INPUT", "MISSING_FILE", "DERIVATION_FAILED">
    message: <human-readable description of what failed and corrective action>

The command exits without invoking the skill. No partial output is written.

### 5.5 Activation Section

```markdown
## Activation

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:tasklist-protocol

Pass the following context:
- Roadmap text: full content of the roadmap file
- Spec text (if provided): full content of the spec file
- Output directory: resolved TASKLIST_ROOT path

Do NOT attempt to generate the tasklist using only this command file.
The full generation algorithm is in the protocol skill.
```

### 5.6 Boundaries

**Will:**
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content
- Invoke the skill with validated context
- Report generated file paths on completion

**Will Not:**
- Execute the generation algorithm (that's the skill's job)
- Modify source roadmap files
- Run `superclaude sprint run` (output is compatible; invocation is separate)
- Generate anything beyond the tasklist bundle

---

## 6. Skill Specification (`sc-tasklist-protocol/SKILL.md`)

### 6.1 Frontmatter

```yaml
---
name: sc:tasklist-protocol
description: "Deterministic roadmap-to-tasklist generator producing Sprint CLI-compatible multi-file bundles with /sc:task-unified compliance tier integration"
category: utility
complexity: high
allowed-tools: Read, Glob, Grep, Write, Bash, TodoWrite
mcp-servers: [sequential, context7]
personas: [analyzer, architect]
argument-hint: "<roadmap-path> [--spec <spec-path>] [--output <output-dir>]"
---
```

### 6.2 Content

The SKILL.md body is the **full v3.0 generator prompt** — sections §0 through §9 plus the Appendix — reformatted into skill convention but functionally identical.

**Structural mapping from v3.0 to SKILL.md:**

| v3.0 Section | SKILL.md Location | Notes |
|---|---|---|
| Header + intro | Frontmatter + opening paragraph | Adapted to skill format |
| §0 Non-Leakage Rules | `## Non-Leakage + Truthfulness Rules` | Verbatim |
| §1 Objective | `## Objective` | Verbatim (already updated for multi-file) |
| §2 Input Contract | `## Input Contract` | Verbatim |
| §3 Artifact Paths + §3.3 File Emission | `## Artifact Paths` | Verbatim; also extracted to `rules/file-emission-rules.md` |
| §4 Generation Algorithm | `## Deterministic Generation Algorithm` | Verbatim |
| §5 Enrichment | `## Deterministic Enrichment` | Verbatim; §5.3 also extracted to `rules/tier-classification.md` |
| §6A Index Template | `## Index File Template` | Verbatim; also extracted to `templates/index-template.md` |
| §6B Phase File Template | `## Phase File Template` | Verbatim; also extracted to `templates/phase-template.md` |
| §7 Style Rules | `## Style Rules` | Verbatim |
| §8 Self-Check | `## Sprint Compatibility Self-Check` | Verbatim |
| §9 Final Output Constraint | `## Final Output Constraint` | Verbatim |
| Appendix | `## Appendix: Tier Classification Quick Reference` | Verbatim |

Note on stage completion reporting (skill packaging addition): The stage completion reporting contract (§4.3) is a reliability mechanism added during skill packaging. It constrains execution behavior without altering the generation algorithm, task schema, or output structure. The v3.0 generator did not include per-stage validation semantics; this is intentional hardening for automated sprint execution contexts.

The following per-stage validation criteria are used for structural gating and observational reporting:

| Stage | Name | Validation Criteria |
|-------|------|---------------------|
| 1 | Input Ingest | Roadmap text non-empty; required sections (phases/items) present; file read succeeded |
| 2 | Parse + Phase Bucketing | Every roadmap item assigned to exactly one phase; no ambiguous assignments remain unresolved; phase count ≥ 1 |
| 3 | Task Conversion | All roadmap items converted to task stubs; T<PP>.<TT> IDs assigned with no collisions; task titles non-empty |
| 4 | Enrichment | All tasks have non-empty: Effort (XS/S/M/L/XL), Risk (low/moderate/high), Tier (STANDARD/STRICT/EXEMPT/LIGHT), Confidence score |
| 5 | File Emission | tasklist-index.md written; all phase files referenced in index exist on disk; no extra phase files written |
| 6 | Self-Check | All Sprint Compatibility Self-Check assertions (§8) pass; no blocking failures |

Structural gate behavior: If a stage's structurally verifiable criteria are not satisfied (e.g., empty output, missing required fields, ID collisions), the skill reports the failed criterion and attempts correction before advancing. Semantic criteria are reported via TodoWrite but do not block advancement.

### 6.3 Extracted Reference Files

These are **read-only reference extracts** — not independent specs. They exist so the skill can `@reference` them without bloating the main SKILL.md, and so humans can review specific aspects in isolation.

| File | Source | Purpose |
|---|---|---|
| `rules/tier-classification.md` | §5.3 + Appendix | Tier keywords, compound phrases, context boosters, verification routing |
| `rules/file-emission-rules.md` | §3.3 | Naming conventions, phase heading format, content boundaries, target directory layout |
| `templates/index-template.md` | §6A | Complete tasklist-index.md template with all sections |
| `templates/phase-template.md` | §6B | Complete phase-N-tasklist.md template with task format, checkpoints |

### 6.4 Tool Usage

| Tool | Usage | Phase |
|------|-------|-------|
| `Read` | Read roadmap, spec, and reference files | Input |
| `Grep` | Scan roadmap for phase labels, version tokens, keywords | Parsing (§4.1-4.3) |
| `Write` | Write `tasklist-index.md` and each `phase-N-tasklist.md` | Output (§6) |
| `TodoWrite` | Track generation progress (parse → enrich → generate → validate) | Throughout |
| `Bash` | Create output directories (`mkdir -p`) | Output |
| `Glob` | Verify output files exist for self-check (§8) | Validation |

### 6.5 MCP Usage

| Server | Usage | When |
|--------|-------|------|
| `sequential` | Structured reasoning for tier classification, conflict resolution | §5.3 tier scoring |
| `context7` | Framework pattern validation if roadmap references specific libraries | §5.3 context boosters |

---

## 7. Installation & Dev Workflow

### 7.1 Installation

After `superclaude install`:
- `tasklist.md` → `~/.claude/commands/sc/tasklist.md`
- `sc-tasklist-protocol/` is NOT copied to `~/.claude/skills/` (it has a paired command, so the installer skips it per `_has_corresponding_command` logic)
- The skill is accessed only via `Skill sc:tasklist-protocol` from within the command

### 7.2 Dev Workflow

```bash
# After editing src/superclaude/commands/tasklist.md or src/superclaude/skills/sc-tasklist-protocol/:
make sync-dev          # Copies to .claude/
make verify-sync       # Confirms sync
make lint-architecture # Validates:
                       #   - tasklist.md has ## Activation section
                       #   - sc-tasklist-protocol/ directory exists
                       #   - SKILL.md has name:, description:, allowed-tools: frontmatter
                       #   - name: field ends in -protocol
```

### 7.3 Lint-Architecture Checks

| Check | Expectation |
|---|---|
| 1 | `tasklist.md` has `## Activation` → `sc-tasklist-protocol/` directory exists |
| 2 | `sc-tasklist-protocol/` exists → `tasklist.md` command exists |
| 3-4 | `tasklist.md` within line limits (warn at 200, fail at 500) |
| 6 | `tasklist.md` has `## Activation` section |
| 8 | `SKILL.md` has `name:`, `description:`, `allowed-tools:` |
| 9 | `name:` field ends in `-protocol` |

---

## 8. Migration from Current State

### 8.1 Files to Create

| File | Source | Action |
|---|---|---|
| `src/superclaude/commands/tasklist.md` | New (based on `TasklistGenPrompt.md` pattern) | Write |
| `src/superclaude/skills/sc-tasklist-protocol/SKILL.md` | `.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md` (v3.0) | Reformat into skill |
| `src/superclaude/skills/sc-tasklist-protocol/__init__.py` | — | Create empty |
| `src/superclaude/skills/sc-tasklist-protocol/rules/tier-classification.md` | Extract from SKILL.md §5.3 + Appendix | Extract |
| `src/superclaude/skills/sc-tasklist-protocol/rules/file-emission-rules.md` | Extract from SKILL.md §3.3 | Extract |
| `src/superclaude/skills/sc-tasklist-protocol/templates/index-template.md` | Extract from SKILL.md §6A | Extract |
| `src/superclaude/skills/sc-tasklist-protocol/templates/phase-template.md` | Extract from SKILL.md §6B | Extract |

### 8.2 Files NOT Modified

- The v3.0 generator prompt stays in `.dev/releases/backlog/v.1.5-Tasklists/` as the source-of-truth reference
- `TasklistGenPrompt.md` stays as historical reference (superseded by `/sc:tasklist`)

### 8.3 Validation Steps

1. `make sync-dev` — copies to `.claude/`
2. `make verify-sync` — confirms sync
3. `make lint-architecture` — validates command/skill pair
4. Manual test: `/sc:tasklist @<roadmap>` produces valid multi-file bundle
5. Sprint test: `superclaude sprint run <generated-index>` discovers all phases

---

## 9. Acceptance Criteria

1. `/sc:tasklist @roadmap.md` is discoverable in Claude Code command palette
2. Running `/sc:tasklist @roadmap.md --output <dir>` produces:
   - `tasklist-index.md` with Phase Files table containing literal filenames
   - `phase-N-tasklist.md` files matching Sprint CLI naming convention
   - All tasks with `T<PP>.<TT>` IDs, tier classifications, and per-task metadata
3. `make lint-architecture` passes with no errors for the new pair
4. `superclaude sprint run <generated-index>` can discover all phase files
5. Generated phase files are lean (no registries, traceability matrix, or templates)
6. Generation executes in stage order (Ingest → Parse/Bucket → Convert → Enrich → Emit → Self-Check). Each stage reports completion via TodoWrite. Structurally verifiable criteria (field presence, ID format, file existence) are checked before advancing; semantic criteria are logged as advisory. Completed stages are reported in order.
7. Functional parity: output is identical to running the v3.0 generator prompt manually
8. Pre-write semantic quality gate passes before any file is written: all tasks have complete metadata fields (Effort, Risk, Tier, Confidence, Verification Method), all Deliverable IDs are globally unique across the bundle, no task has a placeholder description, and every task has at least one R-### Roadmap Item ID assigned.
9. Pre-write semantic and structural quality gates (§8.1, §8.2) pass before any file is written: all tasks have complete metadata fields, all Deliverable IDs are globally unique, no placeholder descriptions exist, every task has traceability, phase sizes are bounded, no circular dependencies, and bundle write is atomic.
10. No output files are written unless Stage 1 through Stage 4 structural validations have passed. Stage 5 (File Emission) is only entered after all pre-write stages report completion.
11. Every generated task description is standalone per §7.N: names a specific artifact or target, contains no external-context references, and uses a concrete action verb with explicit object.

---

## 10. Open Questions

1. **Should `rules/` and `templates/` be `@referenced` from SKILL.md or inlined?**
   Recommendation: Inline in SKILL.md for v1.0, extract files as read-only references for human review. The skill must be self-contained for Claude to execute without additional file reads.

2. **Should the command accept `@file` syntax or explicit path arguments?**
   Recommendation: Support both. `@file` is native Claude Code syntax; explicit paths work for automation.

3. **Should `--output` be required or auto-derived?**
   Recommendation: Auto-derived from roadmap content (§3.1 algorithm) with `--output` as override. This matches current behavior.

4. **Should Write() calls be atomic (all files after validation) or incremental (file by file)?**
   Resolution: Atomic. The §8.1/§8.2 Quality Gates validate the full in-memory bundle before any Write() call. Incremental writing is prohibited to prevent partial bundle states.
