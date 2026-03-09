# D-0009: validate_executor.py Specification

## Module

`src/superclaude/cli/roadmap/validate_executor.py`

## Public API

### `execute_validate(config: ValidateConfig) -> dict`

Orchestrates the full validation workflow.

**Parameters:**
- `config.output_dir` -- directory containing pipeline outputs (roadmap.md, test-strategy.md, extraction.md)
- `config.agents` -- list of AgentSpec; len=1 triggers single-agent mode, len>1 triggers multi-agent

**Returns:** `dict` with `blocking_count`, `warning_count`, `info_count` (all int)

**Raises:** `FileNotFoundError` if any required input file is missing

## Routing Logic

| Agent Count | Steps | Gate | Output |
|-------------|-------|------|--------|
| 1 | reflect | REFLECT_GATE | validate/validation-report.md |
| N | N parallel reflects → adversarial-merge | REFLECT_GATE per agent, ADVERSARIAL_MERGE_GATE on merge | validate/reflect-{id}.md + validate/validation-report.md |

## Infrastructure Reuse

- `execute_pipeline` -- step sequencing, retry, parallel dispatch
- `ClaudeProcess` -- subprocess lifecycle management
- `validate_run_step` -- mirrors `roadmap_run_step` pattern
- `_embed_inputs` / `_sanitize_output` -- reused from roadmap executor pattern

## Verification

```
uv run python -c "from superclaude.cli.roadmap.validate_executor import execute_validate; print('OK')"
# exits 0
```
