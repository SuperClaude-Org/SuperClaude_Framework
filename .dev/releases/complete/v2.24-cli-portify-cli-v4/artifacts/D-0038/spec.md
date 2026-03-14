# D-0038: Resume Command Generation (SC-014)

Resumable failures produce `--start <step>` commands with suggested budget.

## Format

```
superclaude cli-portify run <workflow_path> --start <step> --max-convergence <budget>
```

## Rules

- Only generated for resumable steps (5-7)
- Non-resumable failures (steps 1-4) return empty string
- Suggested budget equals original max_convergence

Implementation: `build_resume_command()` in `src/superclaude/cli/cli_portify/resume.py`
