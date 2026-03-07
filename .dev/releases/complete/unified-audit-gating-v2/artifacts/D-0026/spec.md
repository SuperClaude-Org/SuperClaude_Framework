# D-0026: CHANGELOG Entry for Sprint Runner v2.0.0

## Evidence

**File**: `CHANGELOG.md` (repository root)
**Section**: `[Unreleased]`

### Verification Checklist

- [x] **Changed section** present — documents `max_turns` (50→100) and `reimbursement_rate` (0.5→0.8)
- [x] **Migration Guide section** present — includes explicit override command `superclaude sprint run <index> --max-turns 50`
- [x] **Budget Guidance section** present — recommends `initial_budget ≥ 250` for >40 tasks at rate=0.8
- [x] Follows Keep a Changelog format
- [x] Phase timeout implication documented (6,300s → 12,300s)
- [x] Net cost math included (4 turns per passing task at rate=0.8)

### Captured Entry Text

```markdown
### Changed (Sprint Runner v2.0.0 — Unified Audit Gating)
- **`max_turns`**: Default increased from `50` → `100` per phase
  - Phase timeout increases proportionally: 6,300s → 12,300s
  - Provides adequate headroom for complex phases with trailing gate verification
- **`reimbursement_rate`**: Default changed from `0.5` → `0.8`
  - Budget sustainability improved: 80% of turns reimbursed on PASS vs prior 50%
  - Net cost per passing task: 4 turns (down from ~6 at rate=0.5)
  - 46-task sprint drains ~184 turns from a 200-turn budget (16-turn margin)

### Migration Guide
Users relying on the previous defaults can preserve old behavior with explicit overrides:
- `superclaude sprint run <index> --max-turns 50`
- `superclaude sprint run <index> --reimbursement-rate 0.5`

### Budget Guidance
- For sprints with >40 tasks at rate=0.8: recommend initial_budget ≥ 250
- For sprints with ≤20 tasks: initial_budget=200 provides comfortable margin
```

## Traceability

- **SC-006**: CHANGELOG entry — SATISFIED
- **Roadmap Item**: R-031
- **Panel Consensus Item**: 5
