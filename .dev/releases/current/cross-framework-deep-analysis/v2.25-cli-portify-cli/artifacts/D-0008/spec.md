# D-0008: Workdir Creation and portify-config.yaml Emission Spec

**Task**: T02.04 — Implement Workdir Creation and portify-config.yaml Emission
**Date**: 2026-03-15
**Status**: COMPLETE

---

## Workdir Structure

Created at: `.dev/portify-workdir/<cli_name_snake>/`

Implemented in `src/superclaude/cli/cli_portify/workdir.py::create_workdir()`.

### Directory Layout

```
.dev/
  portify-workdir/
    <cli_name_snake>/        ← created by create_workdir()
      portify-config.yaml    ← emitted by emit_portify_config_yaml()
      validate-config-result.json
      component-inventory.md
      ...step artifacts...
```

### portify-config.yaml Schema

All 4 required fields (per D-0008 spec):

| Field | Type | Description |
|---|---|---|
| `workflow_path` | string (path) | Resolved workflow skill directory |
| `cli_name` | string | Derived kebab-case CLI name |
| `output_dir` | string (path) | Output destination for generated module |
| `workdir_path` | string (path) | Path to this workdir |

Additional fields emitted for downstream steps:
- `cli_name_snake` — snake_case form of cli_name
- `dry_run` — pipeline dry-run flag
- `debug` — debug logging flag
- `max_turns` — maximum Claude subprocess turns
- `stall_timeout` — stall detection threshold (seconds)

### Module Location

```python
# src/superclaude/cli/cli_portify/workdir.py
def create_workdir(config: PortifyConfig, base: Optional[Path] = None) -> Path: ...
def emit_portify_config_yaml(config: PortifyConfig, workdir: Path) -> Path: ...
def _detect_project_root(workflow_path: Path) -> Path: ...
```

### Workdir Isolation

Artifacts are written exclusively to workdir. No source-tree writes during pipeline execution:
- All step output files go to `workdir/<step-name>.*`
- `portify-config.yaml` is the only file written at workdir root
- Source tree is written only at the final emit step (Step 12)

---

## Test Coverage

Functional verification:
```python
from src.superclaude.cli.cli_portify.workdir import create_workdir, emit_portify_config_yaml
workdir = create_workdir(config, base=tmp)
yaml_path = emit_portify_config_yaml(config, workdir)
assert yaml_path.exists()
yaml_text = yaml_path.read_text()
assert "workflow_path:" in yaml_text
assert "cli_name:" in yaml_text
assert "output_dir:" in yaml_text
assert "workdir_path:" in yaml_text
```
