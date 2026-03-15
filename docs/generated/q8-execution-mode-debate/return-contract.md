# Return Contract: Q8 Execution Mode Annotation Debate

## Status: COMPLETE

## Result: Manual (B) with Hybrid advisory import

### Recommendation

**Use Manual annotation as the primary mechanism, with a non-mutating dry-run advisory imported from Hybrid.**

The tasklist generator should NOT automatically set `execution_mode: python`. Instead:

1. The roadmap author explicitly declares `execution_mode: python` in phase metadata when appropriate.
2. The generator passes through the annotation faithfully.
3. During `--dry-run`, the generator emits an advisory when it detects a phase that appears Python-executable but lacks the annotation.

This approach preserves safety (no silent decisions about skipping Claude reasoning), simplicity (no heuristic code to maintain), and user control (explicit declaration), while importing Hybrid's discoverability benefit through the advisory mechanism.

### Scoring Summary

| Variant | Combined Score | Rank |
|---------|---------------|------|
| Manual (B) | 7.77 | 1st |
| Hybrid (C) | 7.71 | 2nd |
| Auto (A) | 5.49 | 3rd |

### Convergence Score: 68%

Below the 70% threshold -- indicating genuine substantive disagreement between approaches. The primary unresolved tension is between workflow friction (favoring Auto) and safety (favoring Manual/Hybrid). The recommendation resolves this by choosing safety-first with a friction-reducing advisory.

### Unresolved Conflicts

1. **Heuristic reliability**: No empirical data exists to validate or invalidate the proposed detection heuristics. The advisory mechanism provides a low-risk way to gather this data.
2. **User adoption**: Whether roadmap authors will actually use `execution_mode` annotations is unknown. The dry-run advisory is the monitoring mechanism.
3. **Sprint executor integration**: The sprint executor must be updated to consume `execution_mode` -- this is a downstream dependency not resolved by this debate.

## Artifacts

| Artifact | Path |
|----------|------|
| Diff Analysis | `/config/workspace/IronClaude/docs/generated/q8-execution-mode-debate/diff-analysis.md` |
| Debate Transcript | `/config/workspace/IronClaude/docs/generated/q8-execution-mode-debate/debate-transcript.md` |
| Base Selection | `/config/workspace/IronClaude/docs/generated/q8-execution-mode-debate/base-selection.md` |
| Refactoring Plan | `/config/workspace/IronClaude/docs/generated/q8-execution-mode-debate/refactor-plan.md` |
| Return Contract | `/config/workspace/IronClaude/docs/generated/q8-execution-mode-debate/return-contract.md` |
