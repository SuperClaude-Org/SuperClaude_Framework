---
name: tasklist
description: "Generate deterministic, Sprint CLI-compatible tasklist bundles from roadmaps with integrated roadmap validation"
category: utility
complexity: high
allowed-tools: Read, Glob, Grep, Write, Bash, TaskCreate, TaskUpdate, TaskList, TaskGet, Task, Skill
mcp-servers: [sequential, context7]
personas: [analyzer, architect]
version: "2.0.0"
---

# /sc:tasklist

Generate a deterministic, Sprint CLI-compatible tasklist bundle from a roadmap file. Transforms roadmap items into phased, execution-ready task files with compliance tier classification and verification routing. After generation, automatically validates the tasklist against the source roadmap, patches any drift, and verifies corrections.

## Triggers

When the user requests roadmap-to-tasklist conversion, sprint planning from a roadmap, or tasklist generation for execution via `superclaude sprint run`.

## Usage

```
/sc:tasklist <roadmap-path> [--spec <spec-path>] [--output <output-dir>]
```

Both `@file` syntax and explicit file paths are supported for `<roadmap-path>` and `--spec`.

## Behavioral Summary

Transforms a roadmap into a Sprint CLI-compatible multi-file tasklist bundle. The command parses arguments, validates inputs, derives the output directory, and invokes the `sc:tasklist-protocol` skill which contains the full generation algorithm. The command itself does not execute any generation logic.

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `<roadmap-path>` | Yes | -- | Path to roadmap file. Accepts `@file` reference or explicit path. |
| `--spec <spec-path>` | No | -- | Supplementary spec/context file for additional generation context. |
| `--output <output-dir>` | No | Auto-derived from roadmap `TASKLIST_ROOT` | Output directory for the tasklist bundle. |

### TASKLIST_ROOT Auto-Derivation

When `--output` is not provided, `TASKLIST_ROOT` is derived from the roadmap content using this 3-step priority algorithm:

1. If the roadmap text contains a substring matching `.dev/releases/current/<segment>/` (first match), use that as `TASKLIST_ROOT`.
2. Else if the roadmap text contains a version token matching `v<digits>(.<digits>)+` (first match), set `TASKLIST_ROOT = .dev/releases/current/<version-token>/`.
3. Else fallback: `TASKLIST_ROOT = .dev/releases/current/v0.0-unknown/`.

## Input Validation

Before invoking the skill, the command validates all inputs. On any validation failure, the command emits an error and exits without invoking the skill. No partial output is written.

**Error format** (2 fields):
```
error_code: <category string>
message: <human-readable description with corrective action>
```

**Validation checks:**

1. **Roadmap file exists and is readable**: `<roadmap-path>` resolves to a readable, non-empty file. Reject 0-byte or whitespace-only files.
   - Error: `error_code: EMPTY_INPUT` / `error_code: MISSING_FILE`
2. **Spec file exists (if provided)**: `--spec` path resolves to a readable file.
   - Error: `error_code: MISSING_FILE`
3. **Output parent directory exists (if provided)**: `--output` parent directory exists and is writable.
   - Error: `error_code: MISSING_FILE`
4. **TASKLIST_ROOT derivation succeeds (if --output not provided)**: The 3-step derivation algorithm produces a valid path.
   - Error: `error_code: DERIVATION_FAILED`

## Activation

**Classification**: STRICT -- multi-file generation operation with compliance tier integration.

**MANDATORY**: Before executing any protocol steps, invoke:
> Skill sc:tasklist-protocol

Pass the following context:
- Roadmap text: full content of the roadmap file
- Spec text (if provided): full content of the spec file
- Output directory: resolved TASKLIST_ROOT path

Do NOT attempt to generate the tasklist using only this command file.
The full generation algorithm is in the protocol skill.

## Examples

```bash
# Basic: generate tasklist from a roadmap
/sc:tasklist @.dev/releases/current/v2.0/roadmap.md

# With supplementary spec context
/sc:tasklist @roadmap.md --spec @specs/auth-system-prd.md

# Explicit output directory
/sc:tasklist @roadmap.md --output .dev/releases/current/v2.1/tasklist/

# Full invocation with all options
/sc:tasklist @.dev/releases/current/v3.0/roadmap.md --spec @specs/v3-prd.md --output .dev/releases/current/v3.0/tasklist/
```

## Boundaries

**Will:**
- Parse and validate input arguments
- Derive TASKLIST_ROOT from roadmap content
- Invoke the skill with validated context
- Report generated file paths on completion
- Validate generated tasklist against source roadmap (via skill stages 7-10)
- Produce validation artifacts in TASKLIST_ROOT/validation/

**Will Not:**
- Execute the generation algorithm (that is the skill's job)
- Modify source roadmap files
- Run `superclaude sprint run` (output is compatible; invocation is separate)
- Generate anything beyond the tasklist bundle and validation artifacts
