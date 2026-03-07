# D-0029: Budget Guidance Note

## Evidence

**File**: `.dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md`
**Location**: After §3.4 proof, before §3.5

### Added Text
```markdown
> **Budget Guidance** (per panel recommendation — Nygard, Round 2):
> The 16-turn margin at `initial_budget=200` is tight for sprints requiring remediation.
> - For sprints with **>40 tasks** at rate=0.8: recommend `initial_budget ≥ 250`
> - For sprints with **≤20 tasks**: `initial_budget=200` provides comfortable margin
> - Override via sprint configuration: `initial_budget: 250`
```

Also present in CHANGELOG.md under `### Budget Guidance` (see D-0026).

### Verification
- Specific numeric recommendation (`≥ 250`) present ✓
- Supporting rationale (16-turn margin) present ✓
- Framed as recommendation (not code change) ✓
- Matches Nygard's Round 2 recommendation ✓

## Traceability
- **Roadmap Item**: R-034
- **Panel Consensus Item**: 3 (Nygard, Round 2)
