---
deliverable: D-0040
task: T05.04
status: PASS
date: 2026-03-09
---

# D-0040: Cross-Reference Warning Mode Verification

## Evidence

Cross-reference validation in `_cross_refs_resolve()` operates in **warning-only
mode** per T02.02. It emits `UserWarning` for unresolved references but returns
`True` (does not block the pipeline).

### Observed Warning

During the T05.03 integration run against `v2.19-roadmap-validate/roadmap.md`:

```
UserWarning: Unresolved cross-reference: 'See section 6' has no matching heading
```

**Result**: Gate still passed. Pipeline was NOT blocked.

### Gate Behavior Verified

| Scenario | Warning Emitted | Gate Blocked | Expected |
|----------|----------------|--------------|----------|
| Valid cross-ref | No | No | Correct |
| Invalid cross-ref ("See section 6") | Yes | No | Correct (warning-only) |
| No cross-refs present | No | No | Correct |

### Artifacts Tested

- `v2.19-roadmap-validate/roadmap.md` — warning emitted, gate passed
- `v2.18-cli-portify-v2/roadmap.md` — no warning, gate passed
- `v2.17-roadmap-reliability/roadmap.md` — no warning, gate passed

No false-positive blocks on any existing artifacts in `.dev/releases/complete/`.
