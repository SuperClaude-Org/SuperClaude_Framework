# D-0045: Developer Documentation — `cli-portify`

## Command Help

```
Usage: superclaude cli-portify [OPTIONS] COMMAND [ARGS]...

  Port inference-based workflows into programmatic CLI pipelines.

Commands:
  run  Execute the cli-portify pipeline on WORKFLOW_PATH.
```

```
Usage: superclaude cli-portify run [OPTIONS] WORKFLOW_PATH

  Execute the cli-portify pipeline on WORKFLOW_PATH.
  WORKFLOW_PATH is the directory containing a SKILL.md file to portify.

Options:
  --output PATH                Output directory for generated artifacts
  --cli-name TEXT              Override derived CLI command name
  --dry-run                    Validate and plan without executing Claude steps
  --skip-review                Skip interactive review gates
  --start TEXT                 Resume from a specific step (e.g. 'synthesize-spec')
  --max-convergence INTEGER    Maximum convergence iterations (default: 3)
  --iteration-timeout INTEGER  Per-iteration timeout in seconds (default: 300)
  --max-turns INTEGER          Maximum turns per Claude subprocess (default: 100)
  --model TEXT                 Claude model to use
  --debug                      Enable debug logging
```

## Example Invocations

### Basic execution
```bash
superclaude cli-portify run ~/.claude/skills/sc-brainstorm-protocol
```

### Dry-run (validation only)
```bash
superclaude cli-portify run ~/.claude/skills/sc-brainstorm-protocol --dry-run
```

### With custom output directory and name
```bash
superclaude cli-portify run ./my-workflow --output ./output --cli-name my-tool
```

### Resume from a failed step
```bash
superclaude cli-portify run ./my-workflow --start synthesize-spec --max-convergence 5
```

## Output Artifacts

The pipeline produces up to 9 artifacts in the output directory:

| # | Artifact | Step | Description |
|---|----------|------|-------------|
| 1 | `validate-config-result.json` | Step 1 | Config validation results with derived names |
| 2 | `component-inventory.md` | Step 2 | Discovered workflow components with frontmatter |
| 3 | `portify-analysis.md` | Step 3 | Workflow analysis with data flow diagrams |
| 4 | `portify-spec.md` | Step 4 | Pipeline design specification |
| 5 | `synthesized-spec.md` | Step 5 | Unified specification (no placeholders) |
| 6 | `brainstorm-gaps.md` | Step 6 | Gap analysis with findings table |
| 7 | `panel-review.md` | Step 7 | Panel review output per iteration |
| 8 | `panel-report.md` | Step 7 | Machine-readable convergence report |
| 9 | `return-contract.json` | Pipeline | Return contract (success/partial/failed/dry_run) |

## Troubleshooting

### 1. Missing Template
**Error**: `Required template not found: release-spec-template.md`
**Cause**: The workflow directory lacks a required template file.
**Fix**: Ensure `release-spec-template.md` exists in the workflow directory.

### 2. Missing Skills (Graceful Fallback)
**Warning**: `/sc:brainstorm skill NOT available, using inline fallback`
**Cause**: The `/sc:brainstorm` skill is not installed.
**Fix**: Install via `superclaude install`. Pipeline continues with inline fallback.

### 3. Malformed Artifact
**Error**: `Malformed artifact: missing frontmatter`
**Cause**: Claude subprocess produced output without YAML frontmatter.
**Fix**: Re-run the step. Increase `--max-turns` if the problem persists.

### 4. Timeout
**Error**: `Step 'panel-review' timed out after 300s`
**Cause**: Claude subprocess exceeded per-iteration timeout.
**Fix**: Increase `--iteration-timeout` (e.g., `--iteration-timeout 600`).

### 5. Partial Artifact
**Error**: `Partial artifact: 2 placeholder(s) remain`
**Cause**: Claude subprocess didn't complete all sections.
**Fix**: Re-run the step. The re-run policy ensures completeness.

### 6. Non-Writable Output
**Error**: `Output directory is not writable`
**Cause**: The output path doesn't exist or lacks write permissions.
**Fix**: Specify a writable `--output` directory.

### 7. Budget Exhausted
**Error**: `Convergence budget exhausted: 3/3 iterations without convergence`
**Cause**: Panel review didn't converge within `--max-convergence` iterations.
**Fix**: Increase `--max-convergence` or review brainstorm-gaps for persistent issues.
