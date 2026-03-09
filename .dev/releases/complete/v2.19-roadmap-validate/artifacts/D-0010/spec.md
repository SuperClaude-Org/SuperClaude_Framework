# D-0010: Partial Failure Handling Specification

## Location

`src/superclaude/cli/roadmap/validate_executor.py` -- `_write_degraded_report()` function

## Behavior

When multi-agent validation fails partially (some agents succeed, others fail):

1. `execute_pipeline` returns with mixed results (some PASS, some FAIL/TIMEOUT)
2. `execute_validate` detects the partial failure
3. `_write_degraded_report` writes `validate/validation-report.md` with:
   - `validation_complete: false` in YAML frontmatter
   - `failed_agents` and `passed_agents` fields
   - Prominent warning banner naming failed agents
   - Status section explaining the degradation
4. Successful agent reflection files are preserved in `validate/`

## Degraded Report Format

```yaml
---
validation_complete: false
blocking_issues_count: 0
warnings_count: 0
failed_agents: reflect-opus-architect
passed_agents: reflect-haiku-architect
---
```

Followed by a `> **WARNING: DEGRADED VALIDATION REPORT**` blockquote banner.

## Design Decision

Per OQ-2: "Silent degradation is unacceptable." The report is unmistakably
marked as incomplete via both frontmatter and visible banner text.
