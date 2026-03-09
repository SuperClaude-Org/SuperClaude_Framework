# D-0016: CLI Output Behavior Spec

## Output Format
- Blocking issues: printed as yellow WARNING via `click.style(fg="yellow")`
- Warning count: printed as plain text
- Info count: printed as plain text
- Summary line: `[validate] Complete: N blocking, N warning, N info`

## Exit Code
- Always 0 regardless of blocking/warning count (per NFR-006)
- No explicit `sys.exit()` call; Click handles normal exit as 0
- Pipeline failures (sys.exit(1)) occur BEFORE validation is reached, not during

## Implementation
- File: `src/superclaude/cli/roadmap/commands.py` (standalone validate command)
- File: `src/superclaude/cli/roadmap/executor.py` (_auto_invoke_validate for roadmap run)
