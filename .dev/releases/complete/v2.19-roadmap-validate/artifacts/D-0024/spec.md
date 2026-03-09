# Roadmap Validate -- Operational Documentation

## Standalone Usage

The `validate` subcommand runs validation against existing pipeline outputs.

```bash
# Basic usage (single-agent, cost-efficient)
superclaude roadmap validate ./output-dir

# Multi-agent adversarial validation
superclaude roadmap validate ./output-dir --agents opus:architect,haiku:qa

# Custom model and debug logging
superclaude roadmap validate ./output-dir --model sonnet --debug
```

**Required inputs**: The output directory must contain three files from a prior `roadmap run`:
- `roadmap.md` -- the merged roadmap
- `test-strategy.md` -- the test strategy
- `extraction.md` -- the requirement extraction

**Output**: Creates a `validate/` subdirectory containing:
- `validation-report.md` -- the consolidated validation report with YAML frontmatter
- Per-agent reflection files (multi-agent mode only): `reflect-{model}-{persona}.md`

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--agents` | `opus:architect` | Comma-separated agent specs (model:persona) |
| `--model` | (none) | Override model for all validation steps |
| `--max-turns` | 100 | Max agent turns per subprocess |
| `--debug` | false | Enable debug logging |

## Multi-Agent Trade-Offs

### Single-Agent Mode (1 agent)

- **Cost**: ~1x token cost (one LLM call)
- **Rigor**: Single perspective; may miss defects that another persona would catch
- **Speed**: Faster (one subprocess)
- **When to use**: Quick validation, cost-sensitive environments, iterative development

### Multi-Agent Mode (2+ agents)

- **Cost**: ~Nx token cost (N parallel reflections + 1 merge step)
- **Rigor**: Multiple perspectives with adversarial merge; agreement categorization (BOTH_AGREE, ONLY_A, ONLY_B, CONFLICT) surfaces disagreements
- **Speed**: Slower (parallel reflections + sequential merge)
- **When to use**: Final validation before tasklist generation, high-stakes roadmaps, when confidence in roadmap quality is critical

### Agreement Categories

| Category | Meaning | Action |
|----------|---------|--------|
| BOTH_AGREE | Finding in all agent reports with consistent severity | High confidence -- include as-is |
| ONLY_A / ONLY_B | Finding in one agent's report only | Review recommended -- may be true or false positive |
| CONFLICT | Finding with different severity across agents | Escalate to BLOCKING |

## --no-validate and --resume Interaction

### Decision Matrix

| Scenario | Validation Runs? | Notes |
|----------|-----------------|-------|
| `roadmap run spec.md` | Yes (auto-invocation) | Runs after all 8 pipeline steps pass |
| `roadmap run spec.md --no-validate` | No | Records "skipped" in state file |
| `roadmap run spec.md --resume` (all steps pass) | Yes | Auto-invokes after completion |
| `roadmap run spec.md --resume` (step fails) | No | Pipeline halts with exit code 1 |
| `roadmap run spec.md --resume` (validation already completed) | No | Skips with "already completed" message |
| `roadmap validate ./output` | Yes (standalone) | Independent of pipeline state |

### State File Interaction

Validation status is persisted in `.roadmap-state.json` under the `validation` key:

```json
{
  "validation": {
    "status": "pass",
    "timestamp": "2026-03-08T12:00:00+00:00"
  }
}
```

Possible status values: `"pass"`, `"fail"`, `"skipped"`

The `--resume` flag checks this state before running validation:
- If `status` is `"pass"` or `"fail"`, validation is skipped (already completed)
- If `status` is `"skipped"` or absent, validation runs normally

## Default Agent Count Asymmetry

### Standalone vs. Roadmap Run Defaults

| Invocation | Default Agents | Count | Rationale |
|-----------|---------------|-------|-----------|
| `roadmap validate ./output` | `opus:architect` | 1 | Cost efficiency for ad-hoc validation |
| `roadmap run spec.md` (auto-invocation) | First 2 from `--agents` | 2 | Higher rigor for pipeline completion |

**Design decision (OQ-1)**: The asymmetry exists because:

1. **Standalone validate** is often used iteratively during development. Running 2 agents each time doubles cost without proportional benefit when the user is actively fixing issues.

2. **Roadmap run auto-invocation** happens once after all 8 pipeline steps complete. This is the "final gate" before tasklist generation, where the cost of missing a defect is higher than the cost of an extra LLM call.

3. Users can always override: `--agents opus:architect,haiku:qa` works in both contexts.
