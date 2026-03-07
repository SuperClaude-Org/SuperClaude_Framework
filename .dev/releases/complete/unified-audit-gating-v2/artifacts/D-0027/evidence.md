# D-0027: Spec §3.1 Rate Update

## Evidence

**File**: `.dev/releases/current/unified-audit-gating-v1.2.1/unified-spec-v1.0.md`
**Line**: 178

### Before
```
reimbursement_rate: float = 0.90  # 90% reimbursement on PASS
```

### After
```
reimbursement_rate: float = 0.80  # 80% reimbursement on PASS
```

### Verification
```
$ grep -n 'reimbursement_rate' unified-spec-v1.0.md
178:    reimbursement_rate: float = 0.80  # 80% reimbursement on PASS
191:        self.reimbursed += math.floor(turns * self.reimbursement_rate)
```

Spec now matches implementation value (`src/superclaude/cli/sprint/models.py:476` → `reimbursement_rate: float = 0.8`).

## Traceability
- **Roadmap Item**: R-032
- **Panel Consensus Item**: 2
