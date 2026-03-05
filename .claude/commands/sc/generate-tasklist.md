---
name: generate-tasklist
description: "Generate Sprint CLI-compatible tasklist bundle from a roadmap using the deterministic generator prompt"
category: utility
complexity: high
allowed-tools: Read, Write, Glob, Grep, Bash, TodoWrite, Task
mcp-servers: [sequential]
personas: [architect, analyzer]
---

# /sc:generate-tasklist - Deterministic Tasklist Generator

## Usage
```
/sc:generate-tasklist <roadmap-path> [--spec <spec-path>] [--output <destination-dir>]
```

### Arguments
- **roadmap-path** (required): Path to the roadmap file to transform
- **--spec**: Optional supplementary specification for resolving ambiguities (not a second roadmap)
- **--output**: Destination directory for the tasklist bundle (default: auto-derived from roadmap per Section 3.1 of the generator)

## Behavioral Summary

Reads the Tasklist Generator Prompt v3.0 and applies it to transform a roadmap into a deterministic, execution-ready multi-file tasklist bundle compatible with `superclaude sprint run` and `/sc:task-unified`.

Output is a file bundle:
- `tasklist-index.md` — Sprint index with metadata, registries, traceability, templates
- `phase-1-tasklist.md` through `phase-N-tasklist.md` — One per phase, execution-focused

## Generator Prompt

Read and follow the generator prompt exactly as written — all sections, rules, output format, and compliance tier classification:

@.dev/releases/backlog/v.1.5-Tasklists/Tasklist-Generator-Prompt-v2.1-unified.md

## Input

**Roadmap** (the ONLY source of truth for generation):

@$ARGUMENTS

## Execution Instructions

1. Parse the generator prompt above as your operating procedure
2. Read the roadmap input referenced above
3. If `--spec` was provided, read it as supplementary context — use it to resolve ambiguities and enrich acceptance criteria, but do NOT treat it as a second roadmap
4. Execute the Deterministic Generation Algorithm (Section 4) against the roadmap
5. Apply Deterministic Enrichment (Section 5) — tier classification, effort/risk, confidence scoring
6. Produce the multi-file bundle per Section 6:
   - Write `tasklist-index.md` with all cross-phase metadata (6A template)
   - Write `phase-N-tasklist.md` for each phase (6B template)
7. Run the Sprint Compatibility Self-Check (Section 8) before finalizing
8. Write all files to the output directory

## Constraints

- Follow the generator prompt's Non-Leakage + Truthfulness Rules (Section 0)
- Preserve all roadmap deliverables — do not drop or merge items without the generator's explicit merge rules
- Create Clarification Tasks for any missing information per Section 4.6
- Every task must have a compliance tier with confidence scoring
- Phase files MUST use `phase-N-tasklist.md` naming convention (Sprint CLI requirement)
- Phase headings MUST be `# Phase N — <Name>` (Sprint CLI TUI extraction requirement)
- Do NOT include completion protocol instructions in phase files (Sprint executor injects those)
- Respect the roadmap's priority wave ordering if present

## Examples

### Generate from a roadmap
```
/sc:generate-tasklist .dev/releases/current/v2.08-roadmap-v4/roadmap.md
```

### With supplementary spec and explicit output
```
/sc:generate-tasklist .dev/releases/current/v2.08-roadmap-v4/roadmap.md --spec .dev/releases/current/v2.08-roadmap-v4/spec.md --output .dev/releases/current/v2.08-roadmap-v4/tasklist/
```

## Boundaries

**Will:**
- Transform any roadmap into a deterministic, Sprint CLI-compatible tasklist bundle
- Apply compliance tier classification with confidence scoring to every task
- Generate Clarification Tasks for missing information
- Produce all required metadata (registries, traceability matrix, templates)

**Will Not:**
- Invent context not present in the roadmap
- Skip the Sprint Compatibility Self-Check
- Output a single monolithic document (must be multi-file bundle)
- Include completion protocol in phase files

**Next Step**: After generation, run `superclaude sprint run <output-dir>/tasklist-index.md` to execute the tasklist.
