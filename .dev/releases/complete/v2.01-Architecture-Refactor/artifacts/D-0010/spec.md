# D-0010 — Spec: Fallback Protocol F1/F2-3/F4-5

**Task**: T02.03
**Date**: 2026-02-24
**Status**: COMPLETE

## Fallback Protocol

The fallback protocol is referenced within Step 3d (line 161) of the SKILL-DIRECT variant:

```
sc:adversarial-protocol executes F1 (variant generation) → F2/3 (diff + debate) → F4/5 (base selection + merge)
```

### F1: Variant Generation
Task agents generate variants (one per expanded agent spec from 3a/3b).

### F2/3: Diff Analysis + Adversarial Debate (Merged Stage)
Diff against spec; parallel advocates → sequential rebuttals.

### F4/5: Base Selection + Merge + Contract (Merged Stage)
Select winning variant (convergence_score driven). Produce return contract.

## 3-Status Convergence Routing (Step 3e)

| Status | Threshold | Action |
|--------|-----------|--------|
| PASS | convergence_score >= 0.6 | Use merged_output_path as roadmap source |
| PARTIAL | convergence_score >= 0.5 | Use merged_output_path with warning (`adversarial_status: partial`) |
| FAIL | convergence_score < 0.5 | Abort roadmap generation |

## Error Handling

- **Missing/empty response**: Fallback convergence_score = 0.5 (forces Partial path)
- **YAML parse error**: Same fallback (convergence_score = 0.5)
- **Skill invocation failure**: Abort with error message

*Artifact produced by T02.03*
