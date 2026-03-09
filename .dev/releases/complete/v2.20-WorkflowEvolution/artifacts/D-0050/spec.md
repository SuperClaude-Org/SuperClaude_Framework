---
deliverable: D-0050
task: T05.13
status: PASS
date: 2026-03-09
---

# Operational Guidance: v2.20 Pipeline Features

## Fidelity Status Meanings

### PASS — Clean Validation

**What it means**: All gate criteria satisfied. No HIGH-severity deviations found.
Zero unexpected issues.

**Output indicators**:
- `tasklist_ready: true` in frontmatter
- `high_severity_count: 0`
- `validation_complete: true`

**User action**: Proceed to next phase or mark release as validated.

### FAIL — Validation Failed

**What it means**: Gate criteria not met after all retries. At least one check
failed (missing frontmatter, line count too low, or semantic check failure).

**Output indicators**:
- Error message in pipeline output: `[step-id] FAIL: <reason>`
- `tasklist_ready: false` (if fidelity step)
- Non-zero `high_severity_count`

**User action**: Read the failure reason, fix the upstream document, and re-run
with `--resume` to skip already-passed steps.

### SKIPPED — Already Validated

**What it means**: Step was not executed because its output already exists and
passes the gate (during `--resume`). Or post-pipeline validation was skipped
due to `--no-validate`.

**Output indicators**:
- `[step-id] SKIP (output already passes gate)`
- `validation_complete: skipped` (for post-pipeline validate)

**User action**: None required. Previous output is still valid.

### DEGRADED — Partial Results

**What it means**: Multi-agent validation where at least one agent succeeded
but another failed or timed out. Results from successful agents are preserved.

**Output indicators**:
- `[validate] DEGRADED: agents failed: [agent-ids]`
- `validation_complete: false`
- Successful agent reports still present in output directory

**User action**: Review successful agent results. Decide whether partial
validation is sufficient or re-run failed agents individually.

## Expected Output Artifacts

### Roadmap Pipeline (`superclaude roadmap run`)

| Artifact | Location | Description |
|----------|----------|-------------|
| extraction.md | `{output_dir}/extraction.md` | Requirements extraction with frontmatter |
| roadmap-{agent}.md | `{output_dir}/roadmap-{agent}.md` | Per-agent roadmap variants |
| diff-analysis.md | `{output_dir}/diff-analysis.md` | Differences between agent roadmaps |
| debate-transcript.md | `{output_dir}/debate-transcript.md` | Adversarial debate record |
| base-selection.md | `{output_dir}/base-selection.md` | Winner selection rationale |
| roadmap.md | `{output_dir}/roadmap.md` | Merged final roadmap |
| test-strategy.md | `{output_dir}/test-strategy.md` | Validation milestones |
| spec-fidelity.md | `{output_dir}/spec-fidelity.md` | Spec→roadmap deviation report |

### Tasklist Validation (`superclaude tasklist validate`)

| Artifact | Location | Description |
|----------|----------|-------------|
| tasklist-fidelity.md | `{output_dir}/tasklist-fidelity.md` | Roadmap→tasklist deviation report |

### Post-Pipeline Validation (`superclaude roadmap validate`)

| Artifact | Location | Description |
|----------|----------|-------------|
| reflect-{agent}.md | `{output_dir}/reflect-{agent}.md` | Per-agent reflection |
| merged-reflection.md | `{output_dir}/merged-reflection.md` | Adversarial merge (multi-agent) |

## Quick Reference: Flag Behavior

| Flag | Effect |
|------|--------|
| `--resume` | Skip passed steps, retry from first failure |
| `--no-validate` | Skip post-pipeline validate (NOT spec-fidelity) |
| `--dry-run` | Print step plan without executing |
| `--retrospective <file>` | Inject advisory context into extraction |
| `--depth quick\|standard\|deep` | Control debate rounds (1/2/3) |

## Cross-References

- Degraded-state semantics: `artifacts/D-0044/spec.md`
- Deviation report format: `docs/reference/deviation-report-format.md`
- Pipeline documentation: `PLANNING.md` § Roadmap Generation Pipeline
- Monitoring metrics: `artifacts/D-0045/spec.md`
- Rollback plan: `artifacts/D-0046/spec.md`
