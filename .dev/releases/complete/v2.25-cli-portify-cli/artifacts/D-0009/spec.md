# D-0009: Component Discovery Algorithm Spec

## Task: T02.05

**Implementation:** `src/superclaude/cli/cli_portify/steps/discover_components.py`

## Component Types and Classification

| Type constant | Value | Matched by |
|--------------|-------|------------|
| `COMPONENT_SKILL` | `"skill"` | `SKILL.md` file in skill directory |
| `COMPONENT_COMMAND` | `"command"` | `.md` files in commands directory |
| `COMPONENT_REF` | `"ref"` | files in `refs/` subdirectory |
| `COMPONENT_RULE` | `"rule"` | files in `rules/` subdirectory |
| `COMPONENT_TEMPLATE` | `"template"` | files in `templates/` subdirectory |
| `COMPONENT_SCRIPT` | `"script"` | files in `scripts/` subdirectory |

## Discovery Algorithm (`_scan_skill_dir`)

1. Scan the resolved workflow (skill) directory.
2. For each recognized subdirectory (`refs/`, `rules/`, `templates/`, `scripts/`): enumerate files and create `ComponentEntry` with `{path, line_count, purpose, component_type}`.
3. Read `SKILL.md` and create a SKILL component entry.
4. For each discovered component, count lines and infer purpose from filename/content.

## Artifact Output (`component-inventory.md`)

Written to `output_dir/component-inventory.md` with YAML frontmatter:

```yaml
---
source_skill: <skill_directory_name>
source_command: <command_name or "">
component_count: <int>
total_lines: <int>
agent_count: <int>
has_command: <bool>
has_skill: <bool>
duration_seconds: <float>
---
```

## Acceptance Criteria

- `component-inventory.yaml` emitted with `{path, lines, purpose, type}` per component.
- Inventory contains at least one component with `type == "skill"`.
- Discovery completes in <60s (SC-002 constraint).

## Test Coverage

- `uv run pytest tests/ -k "test_inventory"` — 6 tests, exits 0
- Full `TestInventory` class, `TestDiscoverComponentsTiming`, `TestComponentDiscovery`

## Source Location

- `src/superclaude/cli/cli_portify/steps/discover_components.py`
