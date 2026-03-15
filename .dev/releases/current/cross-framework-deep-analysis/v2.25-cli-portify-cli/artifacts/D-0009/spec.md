# D-0009: Component Discovery Algorithm Spec

**Task**: T02.05 — Implement Component Discovery and inventory.py
**Date**: 2026-03-15
**Status**: COMPLETE

---

## Component Types

Implemented in `src/superclaude/cli/cli_portify/steps/discover_components.py`.

| Constant | Value | Source |
|---|---|---|
| `COMPONENT_SKILL` | `"skill"` | `SKILL.md` at workflow root |
| `COMPONENT_COMMAND` | `"command"` | Top-level `.md` files (not SKILL.md) |
| `COMPONENT_REF` | `"ref"` | Files in `refs/` subdirectory |
| `COMPONENT_RULE` | `"rule"` | Files in `rules/` subdirectory |
| `COMPONENT_TEMPLATE` | `"template"` | Files in `templates/` subdirectory |
| `COMPONENT_SCRIPT` | `"script"` | Files in `scripts/` subdirectory |

## Discovery Algorithm

`_scan_skill_dir(workflow_dir)`:
1. Check `SKILL.md` at root → add as `COMPONENT_SKILL`
2. Iterate `refs/`, `rules/`, `templates/`, `scripts/` → add files as respective types
3. Scan top-level `.md` files (excluding `SKILL.md`) → add as `COMPONENT_COMMAND`

## ComponentInventory Schema

Per-component entry fields: `{name, path, component_type, line_count, purpose}`

## Agent Extraction (6 patterns)

Extracts agent references from SKILL.md content using 6 compiled regex patterns:

| Pattern | Example |
|---|---|
| `AGENT_PATTERN_BACKTICK` | `` `audit-scanner` (Haiku) `` |
| `AGENT_PATTERN_YAML_ARRAY` | `- quality-engineer` |
| `_AGENT_VERB_PAREN` + `_AGENT_VERB_BARE` | `Spawn agent (backend-architect)`, `Delegate to performance-engineer` |
| `AGENT_PATTERN_USES` | `uses: \`deep-research-agent\`` |
| `AGENT_PATTERN_MODEL_PAREN` | `audit-validator (Sonnet)` |
| `_AGENT_PATH_AGENTS` + `_AGENT_PATH_TYPE` | `agents/frontend-architect`, `Agent type: \`merge-executor\`` |

`AGENT_PATTERNS` list contains 6 compiled `re.Pattern` objects.

## Output Artifact

`component-inventory.md` written to `config.output_dir`:
- YAML frontmatter with: `source_skill`, `component_count`, `total_lines`, `duration_seconds`
- Markdown table of all discovered components

## Module Location

```python
# src/superclaude/cli/cli_portify/steps/discover_components.py
def run_discover_components(config) -> tuple[ComponentInventory, PortifyStepResult]: ...
def extract_agents(content, agents_dir) -> list[AgentEntry]: ...
def deduplicate_agents(auto_agents, cli_override_names, agents_dir) -> list[AgentEntry]: ...
def build_component_tree(resolved) -> ComponentTree: ...
def render_enriched_inventory(tree, duration_seconds, resolution_log=None) -> str: ...
AGENT_PATTERNS: list[re.Pattern]  # 6 entries
```

---

## Test Coverage

Test file: `tests/cli_portify/test_discover_components.py` — 56 tests
- SC-002 timing: completes under 5s
- All 6 component types discovered correctly
- Accurate line counting
- All 6 agent extraction patterns verified
- Missing agent warnings (`WARN_MISSING_AGENTS`)
- CLI override deduplication
- Enriched inventory Markdown rendering (8 frontmatter fields, 5 sections)
