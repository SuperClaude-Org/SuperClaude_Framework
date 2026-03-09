# D-0002: ValidateConfig Dataclass Specification

## Location
`src/superclaude/cli/roadmap/models.py`

## Class Hierarchy
`ValidateConfig` extends `PipelineConfig` (from `pipeline/models.py`).

## Fields

| Field | Type | Source | Default |
|-------|------|--------|---------|
| `output_dir` | `Path` | ValidateConfig (new) | `Path(".")` |
| `agents` | `list[AgentSpec]` | ValidateConfig (new) | `[AgentSpec("opus", "architect"), AgentSpec("haiku", "architect")]` |
| `model` | `str` | PipelineConfig (inherited) | `""` |
| `max_turns` | `int` | PipelineConfig (inherited) | `100` |
| `debug` | `bool` | PipelineConfig (inherited) | `False` |

## Design Decision
`model`, `max_turns`, and `debug` are inherited from `PipelineConfig` rather than redeclared, following DRY and the same pattern used by `RoadmapConfig`.

## Verification
```
uv run python -c "from superclaude.cli.roadmap.models import ValidateConfig; print(ValidateConfig.__dataclass_fields__.keys())"
```
Exits 0 with all 5 fields present.
