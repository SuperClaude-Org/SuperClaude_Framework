# Return Contract -- execution_mode Adversarial Debate

## Status: COMPLETE

## Result

### Recommended Minimal Value Set

```
execution_mode: claude | python | skip
```

| Value | Semantics | Default |
|---|---|---|
| `claude` | Phase executed via Claude subprocess (current behavior) | Yes (implicit when absent) |
| `python` | Shell commands run via subprocess.run() with output capture | No |
| `skip` | Phase not executed; zero-cost deactivation | No |

### Rejected Values (with reasoning)

| Value | Rejection Reason |
|---|---|
| `python-gate` | Conflates execution mechanism with flow control. Gate semantics belong in a separate `condition` field. |
| `hybrid` | Breaks phase-level annotation granularity. Split into separate phases instead. |
| `dry-run` | Duplicates existing `--dry-run` CLI flag on the sprint runner. |
| `manual` | No current use case. Can be added as append-only enum extension when needed. |

### Recommended Evolution Path

When a second gating use case emerges, add a `condition` field to phase metadata rather than a `python-gate` execution mode. This separates mechanism (how to run) from semantics (what the result means).

## Artifacts

| Artifact | Path |
|---|---|
| Diff Analysis | /config/workspace/IronClaude/docs/generated/execution-mode-debate/diff-analysis.md |
| Debate Transcript | /config/workspace/IronClaude/docs/generated/execution-mode-debate/debate-transcript.md |
| Base Selection | /config/workspace/IronClaude/docs/generated/execution-mode-debate/base-selection.md |
| Refactoring Plan | /config/workspace/IronClaude/docs/generated/execution-mode-debate/refactor-plan.md |
| Return Contract | /config/workspace/IronClaude/docs/generated/execution-mode-debate/return-contract.md |

## Convergence Score: 69%

Primary disagreement axis: whether `python-gate` should exist as a first-class value or be decomposed into `execution_mode: python` + a separate `condition` field.

## Unresolved Conflicts

1. **Shell command extraction strategy**: The refactoring plan identifies two approaches (parse from step prose vs. explicit `commands` metadata field). The debate did not resolve which is preferable. Recommendation: use the explicit `commands` field for reliability.

2. **Tier interaction with python mode**: Whether `python` phases should be restricted to EXEMPT tier or remain tier-agnostic. The debate leaned toward orthogonality (tier-agnostic) but acknowledged this needs documentation.

3. **Condition field design**: The recommended evolution path (add `condition` field) was not debated in detail. The expression language, evaluation semantics, and error handling for conditions need their own design discussion when the second gating use case emerges.
