# D-0031 — Spec: Tier 2 Ref Loader Design (`claude -p` Script)

**Task**: T06.02
**Date**: 2026-02-24
**Status**: COMPLETE (Design only — implementation deferred to v2.02)
**Tier**: STANDARD

## Purpose

Design document for the Tier 2 ref file loading mechanism using `claude -p` with `--append-system-prompt`. This addresses policy gap #1 from sprint-spec §16: the 3-tier model references `claude -p` for Tier 2 ref file loading but no design document existed.

**Implementation**: DEFERRED to v2.02. This document captures the design, constraints, and open questions.

## Background: 3-Tier Loading Model

| Tier | Content | Loading Mechanism | Status |
|------|---------|-------------------|--------|
| **Tier 0** | Command files (`.md` in `commands/`) | Claude Code auto-loads on slash command | Implemented |
| **Tier 1** | Protocol skills (`SKILL.md` in `skills/`) | `Skill` tool loads into agent context | Implemented |
| **Tier 2** | Ref files (`rules/`, `templates/`, `scripts/` in skill dirs) | `claude -p` script injection OR `Read` tool | **Design only** |

Tier 2 ref files are supplementary materials that protocol skills may need: scoring rubrics, YAML configurations, templates, validation rules. Currently loaded via `Read` tool within the agent context, which works but consumes context tokens.

## Interface Specification

### Input

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `ref_path` | string | Yes | Path to the ref file relative to skill directory (e.g., `rules/scoring.md`) |
| `skill_dir` | string | Yes | Skill directory name (e.g., `sc-roadmap-protocol`) |
| `prompt` | string | No | Optional task prompt for the sub-agent (default: return file content) |

### Output

| Output | Location | Description |
|--------|----------|-------------|
| `stdout` | Console | Sub-agent's response (prose summary or processed content) |
| `exit_code` | Process | 0 = success, 1 = file not found, 2 = claude -p failure |

### Error Handling

| Error | Code | Recovery |
|-------|------|----------|
| Ref file not found | 1 | Log error, return empty — caller decides fallback |
| `claude -p` not available | 2 | Fall back to `Read` tool (current behavior) |
| SKILL.md too large for injection | 2 | Truncate to first N lines, warn in stderr |
| Subprocess timeout | 2 | Kill after 30s, return timeout error |

## Proposed Shell Script

```bash
#!/usr/bin/env bash
# ref-loader.sh — Tier 2 ref file loader via claude -p
# STATUS: DESIGN ONLY — not implemented

set -euo pipefail

SKILL_DIR="${1:?Usage: ref-loader.sh <skill-dir> <ref-path> [prompt]}"
REF_PATH="${2:?Usage: ref-loader.sh <skill-dir> <ref-path> [prompt]}"
PROMPT="${3:-Return the content of the loaded reference file.}"

# Resolve paths
SKILLS_ROOT="${SUPERCLAUDE_SKILLS_ROOT:-$HOME/.claude/skills}"
FULL_PATH="$SKILLS_ROOT/$SKILL_DIR/$REF_PATH"

# Validate ref file exists
if [ ! -f "$FULL_PATH" ]; then
    echo "ERROR: Ref file not found: $FULL_PATH" >&2
    exit 1
fi

# Check claude binary availability
if ! command -v claude &>/dev/null; then
    echo "ERROR: claude binary not found" >&2
    exit 2
fi

# Inject ref content via --append-system-prompt
REF_CONTENT="$(cat "$FULL_PATH")"
claude -p \
    --append-system-prompt "$REF_CONTENT" \
    "$PROMPT" \
    2>/dev/null

exit $?
```

## Constraints and Limitations

### From T01.01 Probe (D-0001)

1. **Binary Available**: `claude` CLI v2.1.52 exists at `/config/.local/bin/claude`
2. **Runtime Unverified**: `claude -p` with `--append-system-prompt` and large payloads has NOT been empirically tested
3. **Sandbox Concerns**: Subprocess execution may be restricted in some environments
4. **No Round-Trip Test**: The probe confirmed binary existence but did not execute a `claude -p` round-trip

### Size Limits

| Concern | Constraint | Mitigation |
|---------|-----------|------------|
| System prompt size | Unknown limit for `--append-system-prompt` | Test with progressively larger payloads; implement truncation |
| Ref file sizes | Range from ~50 lines (scoring rules) to ~500+ lines (templates) | Most ref files are small; large ones may need chunking |
| Token consumption | Each `claude -p` invocation consumes API tokens | Cache results for repeated ref loads in same session |

### `TOOL_NOT_AVAILABLE` Implications

If the ref content references tools (e.g., "use Grep to find..."), the `claude -p` agent may not have those tools available. The ref loader should be used for **content injection only**, not for tool-dependent execution.

### File System Interaction

The `claude -p` subprocess working directory behavior is unknown:
- Does it inherit the caller's working directory?
- Can it access the same files as the calling agent?
- These questions must be empirically tested before implementation.

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Shell script wrapper | Yes | Simple, portable, no additional dependencies |
| `--append-system-prompt` | Yes | Injects content as system context, not user prompt |
| Fallback to `Read` tool | Yes | Current working behavior; `claude -p` is an optimization |
| Content-only injection | Yes | Avoids `TOOL_NOT_AVAILABLE` issues |
| Implementation timing | v2.02 | Requires empirical testing of `claude -p` runtime |

## Open Questions (for v2.02)

1. What is the maximum payload size for `--append-system-prompt`?
2. Does `claude -p` support structured output (JSON, YAML) or only prose?
3. What tools are available in the `claude -p` context?
4. Can `claude -p` write to the file system?
5. How does `claude -p` handle concurrent invocations?
6. Is there a `--model` flag to control which model handles the prompt?

## Relationship to D-0030 (Cross-Skill Invocation)

This design document corresponds to **Pattern 3** in D-0030. The Tier 2 ref loader is a specific application of the `claude -p` invocation pattern for loading supplementary content (rather than full skill protocols).

The decision rule from D-0030 applies:
- Pattern 3 is deferred → use `Read` tool (Pattern 1 fallback) for Tier 2 ref loading until v2.02

*Artifact produced by T06.02 — Design only, implementation deferred to v2.02*
