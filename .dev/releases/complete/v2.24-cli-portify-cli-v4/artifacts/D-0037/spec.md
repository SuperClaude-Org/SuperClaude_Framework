# D-0037: Resumability Matrix

Maps each pipeline step to its resume requirements.

| Step | # | Resumable | Required Artifacts | Preserved Context |
|------|---|-----------|-------------------|-------------------|
| validate-config | 1 | No | — | — |
| discover-components | 2 | No | — | — |
| analyze-workflow | 3 | No | component-inventory.md | — |
| design-pipeline | 4 | No | portify-analysis.md, component-inventory.md | — |
| synthesize-spec | 5 | Yes | portify-analysis.md, portify-spec.md | portify-analysis.md, portify-spec.md |
| brainstorm-gaps | 6 | Yes | synthesized-spec.md | synthesized-spec.md, focus-findings.md |
| panel-review | 7 | Yes | synthesized-spec.md, brainstorm-gaps.md | synthesized-spec.md, brainstorm-gaps.md, focus-findings.md |

Implementation: `src/superclaude/cli/cli_portify/resume.py` — `RESUMABILITY_MATRIX` dict.
